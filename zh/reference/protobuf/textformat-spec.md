+++
title = "文本格式语言规范"
weight = 820
description = "Protobuf 文本格式语言规定了以文本形式表示 Protobuf 数据的语法，这在配置或测试场景中往往很有用。"
type = "docs"
source_url = "https://protobuf.dev/reference/protobuf/textformat-spec/"
upstream_commit = "f72a6a648b34e9e098cbce1519bc9c8139105d66"
translated_at = "2026-11-19"
status = "translated"
translator = "agent"
+++

举例来说，这一格式不同于 `.proto` 模式（schema）中文本所采用的格式。本文档包含的参考文档采用 [ISO/IEC 14977 扩展巴科斯-瑙尔范式（EBNF）](https://en.wikipedia.org/wiki/Extended_Backus%E2%80%93Naur_Form) 所规定的语法。

{{% alert title="Note" color="note" %}}
本规范初稿最初是从 C++ 文本格式（text format）
[实现](https://github.com/protocolbuffers/protobuf/blob/master/src/google/protobuf/text_format.cc)
逆向工程得出的。它历经演进，并可能基于讨论与评审进一步变化。虽然各方已努力在
各受支持的语言之间保持文本格式的一致，但不兼容之处仍可能存在。 {{% /alert %}}

## 示例 {#example}

```textproto
convolution_benchmark {
  label: "NHWC_128x20x20x56x160"
  input {
    dimension: [128, 56, 20, 20]
    data_type: DATA_HALF
    format: TENSOR_NHWC
  }
}
```

## 解析概览 {#parsing}

本规范中的语言元素分为词法（lexical）与句法（syntactic）两类。词法元素必须按描述与输入文本精确匹配，而句法元素之间则可以由可选的 `WHITESPACE` 和 `COMMENT` 记号（token）分隔。

例如，一个带符号的浮点值由两个句法元素组成：符号（`-`）和 `FLOAT` 字面量。在符号与数字之间可以出现可选的空白和注释，但数字内部不行。示例：

```textproto
value: -2.0   # 有效：没有额外的空白。
value: - 2.0  # 有效：'-' 与 '2.0' 之间有空白。
value: -
  # 注释
  2.0         # 有效：'-' 与 '2.0' 之间有空白和注释。
value: 2 . 0  # 无效：浮点数的小数点属于词法
              # 元素的一部分，因此不允许额外的空白。
```

有一个需要特别注意的边界情况：数字记号（`FLOAT`、`DEC_INT`、`OCT_INT` 或 `HEX_INT`）后面不能紧跟一个 `IDENT` 记号。示例：

```textproto
foo: 10 bar: 20           # 有效：空白分隔了 '10' 和 'bar'
foo: 10,bar: 20           # 有效：',' 分隔了 '10' 和 'bar'
foo: 10[com.foo.ext]: 20  # 有效：'10' 后面紧跟 '['，后者
                          # 不是标识符。
foo: 10bar: 20            # 无效：'10' 与标识符 'bar' 之间没有空格。
```

## 词法元素 {#lexical}

下文描述的词法元素分为两类：大写的主元素（primary element）与小写的片段（fragment）。只有主元素会进入句法分析所用的记号输出流；片段的存在只是为了简化主元素的构造。

在解析输入文本时，匹配最长的主元素胜出。示例：

```textproto
value: 10   # '10' 被解析为 DEC_INT 记号。
value: 10f  # '10f' 被解析为 FLOAT 记号，尽管其中的 '10'
            # 也能匹配 DEC_INT。在这个例子中，FLOAT 匹配了
            # 输入中更长的一段子序列。
```

### 字符 {#characters}

```
char    = ? Any non-NUL unicode character ? ;
newline = ? ASCII #10 (line feed) ? ;

letter = "A" | "B" | "C" | "D" | "E" | "F" | "G" | "H" | "I" | "J" | "K" | "L" | "M"
       | "N" | "O" | "P" | "Q" | "R" | "S" | "T" | "U" | "V" | "W" | "X" | "Y" | "Z"
       | "a" | "b" | "c" | "d" | "e" | "f" | "g" | "h" | "i" | "j" | "k" | "l" | "m"
       | "n" | "o" | "p" | "q" | "r" | "s" | "t" | "u" | "v" | "w" | "x" | "y" | "z"
       | "_" ;

oct = "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" ;
dec = "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9" ;
hex = "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9"
    | "A" | "B" | "C" | "D" | "E" | "F"
    | "a" | "b" | "c" | "d" | "e" | "f" ;
```

一组有限的 URL 字符，遵循 [RFC 3986：统一资源标识符（URI）](https://www.rfc-editor.org/rfc/rfc3986#appendix-A)：

```
url_unreserved  = letter | dec | "-" | "." | "~" | "_"
url_sub_delim   = "!" | "$" | "&" | "(" | ")"
                | "*" | "+" | "," | ";" | "="
url_pct_encoded = "%" hex hex
url_char        = url_unreserved | url_sub_delim | url_pct_encoded
```

### 空白与注释 {#whitespace}

```
COMMENT    = "#", { char - newline }, [ newline ] ;
WHITESPACE = " "
           | newline
           | ? ASCII #9  (horizontal tab) ?
           | ? ASCII #11 (vertical tab) ?
           | ? ASCII #12 (form feed) ?
           | ? ASCII #13 (carriage return) ? ;
```

### 标识符 {#identifiers}

```
IDENT = letter, { letter | dec } ;
```

### 数字字面量 {#numeric}

```
dec_lit   = "0"
          | ( dec - "0" ), { dec } ;
float_lit = ".", dec, { dec }, [ exp ]
          | dec_lit, ".", { dec }, [ exp ]
          | dec_lit, exp ;
exp       = ( "E" | "e" ), [ "+" | "-" ], dec, { dec } ;

DEC_INT   = dec_lit
OCT_INT   = "0", oct, { oct } ;
HEX_INT   = "0", ( "X" | "x" ), hex, { hex } ;
FLOAT     = float_lit, [ "F" | "f" ]
          | dec_lit,   ( "F" | "f" ) ;
```

十进制整数可以使用 `F` 和 `f` 后缀转换为浮点值。示例：

```textproto
foo: 10    # 这是一个整数值。
foo: 10f   # 这是一个浮点值。
foo: 1.0f  # 对于浮点字面量，该后缀同样是可选的。
```

### 字符串字面量 {#string}

```
STRING = single_string | double_string ;
single_string = "'", { escape | char - "'" - newline - "\" }, "'" ;
double_string = '"', { escape | char - '"' - newline - "\" }, '"' ;

escape = "\a"                        (* ASCII #7（响铃）                  *)
       | "\b"                        (* ASCII #8（退格）                 *)
       | "\f"                        (* ASCII #12（换页）                *)
       | "\n"                        (* ASCII #10（换行）                *)
       | "\r"                        (* ASCII #13（回车）                *)
       | "\t"                        (* ASCII #9（水平制表符）           *)
       | "\v"                        (* ASCII #11（垂直制表符）          *)
       | "\?"                        (* ASCII #63（问号）                *)
       | "\\"                        (* ASCII #92（反斜杠）              *)
       | "\'"                        (* ASCII #39（撇号）                *)
       | '\"'                        (* ASCII #34（引号）                *)
       | "\", oct, [ oct, [ oct ] ]  (* 八进制转义的字节值               *)
       | "\x", hex, [ hex ]          (* 十六进制转义的字节值             *)
       | "\u", hex, hex, hex, hex    (* 最大到 0xffff 的 Unicode 码点    *)
       | "\U000",
         hex, hex, hex, hex, hex     (* 最大到 0xfffff 的 Unicode 码点   *)
       | "\U0010",
         hex, hex, hex, hex ;        (* 介于 0x100000 与 0x10ffff 之间的 Unicode 码点 *)
```

八进制转义序列最多消耗三个八进制数字，多出的数字不加转义地原样通过。例如，在对输入 `\1234` 进行反转义时，解析器消耗三个八进制数字（123），反转义出字节值 0x53（ASCII 的 'S'，十进制 83），而随后的 '4' 则按字节值 0x34（ASCII 的 '4'）原样通过。为确保解析正确，请用 3 个八进制数字来书写八进制转义序列，必要时使用前导零，例如：`\000`、`\001`、`\063`、`\377`。当数字字符后面跟着非数字字符时，消耗的数字会少于三个，例如 `\5Hello`。

十六进制转义序列最多消耗两个十六进制数字。例如，在对 `\x213` 进行反转义时，解析器只消耗前两个数字（21），反转义出字节值 0x21（ASCII 的 '!'）。为确保解析正确，请用 2 个十六进制数字来书写十六进制转义序列，必要时使用前导零，例如：`\x00`、`\x01`、`\xFF`。当数字字符后面跟着非十六进制字符时，消耗的数字会少于两个，例如 `\xFHello` 或 `\x3world`。

逐字节转义（byte-wise escaping）只应用于类型为 `bytes` 的字段。虽然在类型为 `string` 的字段中也可以使用逐字节转义，但这些转义序列必须组成有效的 UTF-8 序列，而用逐字节转义来表达 UTF-8 序列很容易出错。对于 `string` 类型字段的字面量中的不可打印字符与换行类字符，应优先使用 Unicode 转义序列。

较长的字符串可以在连续的数行上拆分为多个带引号的字符串。例如：

```proto
  quote:
      "When we got into office, the thing that surprised me most was to find "
      "that things were just as bad as we'd been saying they were.\n\n"
      "  -- John F. Kennedy"
```

Unicode 码点（code point）按照 [Unicode 13 表 A-1 扩展巴科斯-瑙尔范式](https://www.unicode.org/versions/Unicode13.0.0/appA.pdf#page=5) 进行解释，并编码为 UTF-8。

{{% alert title="Warning" color="warning" %}} C++ 实现目前会把转义后的高代理项（high-surrogate）码点
解释为 UTF-16 码元，并期望紧随其后出现一个 `\uHHHH` 低代理项码点，
且不允许拆分到不同的带引号字符串中。此外，未配对的代理项会被直接
渲染成同样无效的 UTF-8。这两种行为都不符合规范[^surrogates]，不应依赖。 {{% /alert %}}

[^surrogates]: 参见 Unicode 13
    [§3.8 代理项](https://www.unicode.org/versions/Unicode13.0.0/ch03.pdf#page=48)、
    [§3.2 一致性要求，C1](https://www.unicode.org/versions/Unicode13.0.0/ch03.pdf#page=8)
    以及
    [§3.9 Unicode 编码形式，D92](https://www.unicode.org/versions/Unicode13.0.0/ch03.pdf#page=54)。

## 句法元素 {#syntax}

### 消息 {#message}

消息（message）是字段（field）的集合。一个文本格式文件就是单个 Message。

```
Message = { Field } ;
```

### 字面量 {#literals}

字段的字面量值可以是数字、字符串或标识符（identifier），例如 `true` 或枚举（enum）值。

```
String             = STRING, { STRING } ;
Float              = [ "-" ], FLOAT ;
Identifier         = IDENT ;
SignedIdentifier   = "-", IDENT ;   (* 例如 "-inf" *)
DecSignedInteger   = "-", DEC_INT ;
OctSignedInteger   = "-", OCT_INT ;
HexSignedInteger   = "-", HEX_INT ;
DecUnsignedInteger = DEC_INT ;
OctUnsignedInteger = OCT_INT ;
HexUnsignedInteger = HEX_INT ;
```

单个字符串值可以由多个带引号的部分组成，各部分之间可以用可选的空白分隔。示例：

```textproto
a_string: "first part" 'second part'
          "third part"
no_whitespace: "first""second"'third''fourth'
```

### 字段名 {#field-names}

属于所在消息的字段使用简单的 `Identifiers` 作为名称。[扩展（extension）](/programming-guides/proto2#extensions)与 [`Any`](/programming-guides/proto3#any) 字段名则包裹在方括号中，并且是完全限定（fully-qualified）的。`Any` 字段名是 URI 后缀引用，也就是说，它们以一个起限定作用的 authority 和一个可选的路径作为前缀，例如 `type.googleapis.com/`。

```
FieldName     = ExtensionName | AnyName | IDENT ;
ExtensionName = "[", TypeName, "]" ;
AnyName       = "[", UrlPrefix, "/", TypeName, "]" ;
TypeName      = IDENT, { ".", IDENT } ;
UrlPrefix     = url_char, { url_char | "/" } ;
```

文本格式序列化器不应在 `ExtensionName` 或 `AnyName` 的方括号之间写入任何空白字符或注释。解析器应跳过 `ExtensionName` 或 `AnyName` 方括号之间的任何空白字符与注释，包括把名称拆分成多段的空白和注释。

普通字段和扩展字段可以有标量（scalar）值或消息值。`Any` 字段始终是消息。示例：

```textproto
reg_scalar: 10
reg_message { foo: "bar" }

[com.foo.ext.scalar]​: 10
[com.foo.ext.message] { foo: "bar" }

any_value {
  [type.googleapis.com/com.foo.any] { foo: "bar" }
}
```

#### 未知字段 {#unknown-fields}

文本格式解析器无法支持用原始字段编号代替字段名来表示的未知字段（unknown fields），因为六种线路类型（wire type）中有三种在文本格式中的表示方式相同。一些文本格式序列化器实现会用“字段编号加数值表示”的格式来编码未知字段，但这天生是有损的，因为线路类型信息被忽略了。相比之下，线路格式（wire format）是无损的，因为它把线路类型包含在每个字段标签（tag）中，即 `(field_number << 3) | wire_type`。有关编码（encoding）的更多信息，请参阅[编码](/programming-guides/encoding.md)主题。

如果缺少来自消息模式的字段类型信息，就无法把这个值正确编码到线路格式的 proto 消息中。

### 字段 {#fields}

字段值可以是字面量（字符串、数字或标识符），也可以是嵌套消息。

```
Field        = ScalarField | MessageField ;
MessageField = FieldName, [ ":" ], ( MessageValue | MessageList ) [ ";" | "," ];
ScalarField  = FieldName, ":",     ( ScalarValue  | ScalarList  ) [ ";" | "," ];
MessageList  = "[", [ MessageValue, { ",", MessageValue } ], "]" ;
ScalarList   = "[", [ ScalarValue,  { ",", ScalarValue  } ], "]" ;
MessageValue = "{", Message, "}" | "<", Message, ">" ;
ScalarValue  = String
             | Float
             | Identifier
             | SignedIdentifier
             | DecSignedInteger
             | OctSignedInteger
             | HexSignedInteger
             | DecUnsignedInteger
             | OctUnsignedInteger
             | HexUnsignedInteger ;
```

字段名与值之间的 `:` 分隔符对标量字段是必需的，对消息字段（包括列表）则是可选的。示例：

```textproto
scalar: 10          # 有效
scalar  10          # 无效
scalars: [1, 2, 3]  # 有效
scalars  [1, 2, 3]  # 无效
message: {}         # 有效
message  {}         # 有效
messages: [{}, {}]  # 有效
messages  [{}, {}]  # 有效
```

消息字段的值可以用花括号或尖括号包裹：

```textproto
message: { foo: "bar" }
message: < foo: "bar" >
```

标记为 `repeated` 的字段可以有多个值：可以通过重复该字段、使用特殊的 `[]` 列表语法，或两者结合来指定。值的顺序会得到保留。示例：

```textproto
repeated_field: 1
repeated_field: 2
repeated_field: [3, 4, 5]
repeated_field: 6
repeated_field: [7, 8, 9]
```

等价于：

```textproto
repeated_field: [1, 2, 3, 4, 5, 6, 7, 8, 9]
```

非 `repeated` 字段不能使用列表语法。例如，`[0]` 对 `optional` 或 `required` 字段无效。标记为 `optional` 的字段可以省略或恰好指定一次；标记为 `required` 的字段必须恰好指定一次。`required` 是 proto2 的遗留特性，在 proto3 中不可用。在版次（Editions）中，消息可以通过 [`features.field_presence = LEGACY_REQUIRED`](/editions/features#field_presence) 获得向后兼容（backward compatibility）。

关联 *.proto* 消息中未定义的字段不允许出现，除非该字段名出现在消息的 `reserved` 字段列表中。`reserved` 字段如果以任何形式（标量、列表、消息）出现，文本格式都会直接将其忽略。

## 值类型 {#value}

当字段在关联 *.proto* 文件中的值类型已知时，将适用以下取值描述与约束。为本节的目的，我们声明以下容器元素：

```
signedInteger   = DecSignedInteger | OctSignedInteger | HexSignedInteger ;
unsignedInteger = DecUnsignedInteger | OctUnsignedInteger | HexUnsignedInteger ;
integer         = signedInteger | unsignedInteger ;
```

<table>
  <thead>
    <tr>
      <th style="text-align:center"><strong>.proto 类型</strong></th>
      <th style="text-align:center"><strong>取值</strong></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td style="text-align:center">
        <code>float</code>、<code>double</code>
      </td>
      <td style="text-align:left">
        <code>Float</code>、<code>DecSignedInteger</code> 或
        <code>DecUnsignedInteger</code> 元素；或者是 <code>Identifier</code>
        或 <code>SignedIdentifier</code> 元素，其 <code>IDENT</code>
        部分等于 <em>"inf"</em>、<em>"infinity"</em> 或
        <em>"nan"</em>（不区分大小写）。溢出会被当作无穷大或负无穷大处理。八进制与十六进制值无效。
        <p>
        注意：<em>"nan"</em> 应被解释为 <a href="https://en.wikipedia.org/wiki/NaN#Quiet_NaN">静默 NaN（Quiet NaN）</a>
        </p>
      </td>
    </tr>
    <tr>
      <td style="text-align:center">
        <code>int32</code>、<code>sint32</code>、<code>sfixed32</code>
      </td>
      <td style="text-align:left">
        <em>-0x80000000</em> 至 <em>0x7FFFFFFF</em> 范围内的任一
        <code>integer</code> 元素。
      </td>
    </tr>
    <tr>
      <td style="text-align:center">
        <code>int64</code>、<code>sint64</code>、<code>sfixed64</code>
      </td>
      <td style="text-align:left">
        <em>-0x8000000000000000</em> 至 <em>0x7FFFFFFFFFFFFFFF</em> 范围内的任一
        <code>integer</code> 元素。
      </td>
    </tr>
    <tr>
      <td style="text-align:center">
        <code>uint32</code>、<code>fixed32</code>
      </td>
      <td style="text-align:left">
        <em>0</em> 至 <em>0xFFFFFFFF</em> 范围内的任一
        <code>unsignedInteger</code> 元素。注意，带符号的值
        （<em>-0</em>）无效。
      </td>
    </tr>
    <tr>
      <td style="text-align:center">
        <code>uint64</code>、<code>fixed64</code>
      </td>
      <td style="text-align:left">
        <em>0</em> 至 <em>0xFFFFFFFFFFFFFFFF</em> 范围内的任一
        <code>unsignedInteger</code> 元素。注意，带符号的
        值（<em>-0</em>）无效。
      </td>
    </tr>
    <tr>
      <td style="text-align:center">
        <code>string</code>
      </td>
      <td style="text-align:left">
        包含有效 UTF-8 数据的 <code>String</code> 元素。任何转义序列在反转义后都必须构成有效的 UTF-8 字节序列。
      </td>
    </tr>
    <tr>
      <td style="text-align:center">
        <code>bytes</code>
      </td>
      <td style="text-align:left">
        <code>String</code> 元素，其中可以包含无效的 UTF-8 转义序列。
      </td>
    </tr>
    <tr>
      <td style="text-align:center">
        <code>bool</code>
      </td>
      <td style="text-align:left">
        与下列值之一匹配的 <code>Identifier</code> 元素或任一
        <code>unsignedInteger</code> 元素。<br/>
        <strong>真值：</strong><em>"True"</em>、<em>"true"</em>、
        <em>"t"</em>、<em>1</em><br/>
        <strong>假值：</strong><em>"False"</em>、<em>"false"</em>、
        <em>"f"</em>、<em>0</em><br/>
        <em>0</em> 或 <em>1</em> 的任何无符号整数表示形式都是允许的：<em>00</em>、<em>0x0</em>、<em>01</em>、
        <em>0x1</em> 等。
      </td>
    </tr>
    <tr>
      <td style="text-align:center">
        <em>枚举值</em>
      </td>
      <td style="text-align:left">
        包含枚举值名称的 <code>Identifier</code> 元素；或者是
        <em>-0x80000000</em> 至 <em>0x7FFFFFFF</em> 范围内、包含枚举值编号的任一
        <code>integer</code> 元素。指定的名称若不是该字段
        <code>enum</code> 类型定义的成员，则无效。指定的编号若不是该字段的
        <code>enum</code> 类型定义的成员，是否有效取决于具体的 Protobuf 运行时（runtime）实现。不绑定特定运行时实现的
        文本格式处理器（例如 IDE 支持）可以选择在提供的编号值不是有效成员时发出警告。注意，某些在其他上下文中属于有效关键字的名称，例如
        <em>"true"</em> 或 <em>"infinity"</em>，也可以是有效的枚举值名称。
        <p>
        对于带 <code>allow_aliasing</code> 的枚举，序列化器必须为给定数值打印第一个列出的名称，而解析器必须接受其中任何一个名称。这使得一种安全的重命名策略成为可能，类似于
        <a href="/programming-guides/json#enum-aliasing">ProtoJSON 枚举别名文档</a>中描述的策略。
        </p>
      </td>
    </tr>
    <tr>
      <td style="text-align:center">
        <em>消息值</em>
      </td>
      <td style="text-align:left">
        一个 <code>MessageValue</code> 元素。
      </td>
    </tr>
  </tbody>
</table>

## 扩展字段 {#extension}

扩展字段通过其限定名称来指定。示例：

```textproto
local_field: 10
[com.example.ext_field]​: 20
```

扩展字段通常定义在其他 *.proto* 文件中。文本格式语言没有提供指定扩展字段所在文件位置的机制；相反，解析器必须事先知道这些位置。

## `Any` 字段 {#any}

文本格式支持 [`google.protobuf.Any`](/programming-guides/proto3#any)
知名类型（well-known type）的一种展开形式，它使用一种类似于扩展字段的特殊语法。示例：

```textproto
local_field: 10

# 一个使用普通字段的 Any 值。
any_value {
  type_url: "type.googleapis.com/com.example.SomeType"
  value: "\x0a\x05hello"  # com.example.SomeType 序列化后的字节
}

# 使用 Any 展开形式的同一个值
any_value {
  [type.googleapis.com/com.example.SomeType] {
    field1: "hello"
  }
}
```

在这个例子中，`any_value` 是一个类型为 `google.protobuf.Any` 的字段，它存储了一条序列化的 `com.example.SomeType` 消息，其中包含 `field1: hello`。

## `group` 字段 {#group}

在文本格式中，`group` 字段使用普通的 `MessageValue` 元素作为其值，但要用首字母大写的组名（group name）来指定，而不是隐式的小写字段名。示例：

```proto
// proto2
message MessageWithGroup {
  optional group MyGroup = 1 {
    optional int32 my_value = 1;
  }
}
```

有了上述 *.proto* 定义，下面的文本格式就是一个有效的 `MessageWithGroup`：

```textproto
MyGroup {
  my_value: 1
}
```

与消息字段类似，组名与值之间的 `:` 分隔符同样是可选的。

这一功能被纳入版次（Editions）是为了向后兼容。通常情况下，`DELIMITED` 字段会像普通消息一样序列化。下面展示了版次下的行为：

```proto
edition = "2024";

message Parent {
  message GroupLike {
    int32 foo = 1;
  }
  GroupLike grouplike = 1 [features.message_encoding = DELIMITED];
}
```

该 *.proto* 文件的内容会像 proto2 组（group）一样被序列化：

```proto
GroupLike {
  foo: 2;
}
```

## `map` 字段 {#map}

文本格式没有为指定 map 字段的条目提供自定义语法。当 *.proto* 文件中定义了一个 `map` 字段时，会隐式定义一个包含 `key` 和 `value` 字段的 `Entry` 消息。map 字段始终是可重复的（repeated），可以接受多个键/值（key/value）条目。示例：

```proto
// Editions 语法
edition = "2024";

message MessageWithMap {
  map<string, int32> my_map = 1;
}
```

有了上述 *.proto* 定义，下面的文本格式就是一个有效的 `MessageWithMap`：

```textproto
my_map { key: "entry1" value: 1 }
my_map { key: "entry2" value: 2 }

# 你也可以使用列表语法
my_map: [
  { key: "entry3" value: 3 },
  { key: "entry4" value: 4 }
]
```

`key` 和 `value` 字段都是可选的，未指定时默认为其各自类型的零值。如果键重复，解析后的 map 中只保留最后指定的值。

文本格式文件不保留 map 的顺序。

## `oneof` 字段 {#oneof}

虽然文本格式中没有与 `oneof` 字段相关的特殊语法，但一次只能指定一个 `oneof` 成员；同时指定多个成员是无效的。示例：

```proto
// Editions 语法
edition = "2024";

message OneofExample {
  message MessageWithOneof {
    string not_part_of_oneof = 1;
    oneof Example {
      string first_oneof_field = 2;
      string second_oneof_field = 3;
    }
  }
  repeated MessageWithOneof message = 1;
}
```

上述 *.proto* 定义会产生如下文本格式行为：

```textproto
# 有效：Example oneof 中只设置了一个字段。
message {
  not_part_of_oneof: "always valid"
  first_oneof_field: "valid by itself"
}

# 有效：设置了另一个 oneof 字段。
message {
  not_part_of_oneof: "always valid"
  second_oneof_field: "valid by itself"
}

# 无效：Example oneof 中的多个字段被同时设置。
message {
  not_part_of_oneof: "always valid"
  first_oneof_field: "not valid"
  second_oneof_field: "not valid"
}
```

## 文本格式文件 {#text-format-files}

文本格式文件使用 `.txtpb` 文件名后缀，其中包含单个 `Message`。文本格式文件采用 UTF-8 编码。下面给出了一个 textproto 文件示例。

{{% alert title="Important" color="warning" %}}
`.txtpb` 是规范的文本格式文件扩展名，应优先于其他备选扩展名使用。首选这一后缀是因为它简洁，并与官方线路格式文件扩展名 `.binpb` 保持一致。旧式的规范化（canonical）扩展名
`.textproto` 仍有广泛的使用和工具
支持；一些工具也
支持旧式扩展名 `.textpb` 和 `.pbtxt`。除上述扩展名之外的所有其他扩展名都**强烈**不建议使用；特别是，`.protoascii`
之类的扩展名错误地暗示文本格式仅支持 ASCII，而 `.pb.txt`
之类的扩展名则不被常见工具识别。 {{% /alert %}}

```textproto
# 这是 Protobuf 文本格式的一个示例。
# 与 .proto 文件不同，这里只支持 shell 风格的行注释。

name: "John Smith"

pet {
  kind: DOG
  name: "Fluffy"
  tail_wagginess: 0.65f
}

pet <
  kind: LIZARD
  name: "Lizzy"
  legs: 4
>

string_value_with_escape: "valid \n escape"
repeated_values: [ "one", "two", "three" ]
```

### 文件头 {#header}

头部注释 `proto-file` 和 `proto-message` 向开发工具告知消息的模式，使这些工具能够提供各种特性。

```textproto
# proto-file: some/proto/my_file.proto
# proto-message: MyMessage
```

## 以编程方式处理文本格式

由于各个 Protobuf 实现输出的文本格式既不一致、也不是规范化（canonical）的形式，修改 TextProto 文件或生成 TextProto 输出的工具与库必须显式使用
https://github.com/protocolbuffers/txtpbfmt
来格式化其输出。

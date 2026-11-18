+++
title = "编码"
weight = 60
description = "解释 Protobuf 如何将数据编码到文件或线路。"
type = "docs"
source_url = "https://protobuf.dev/programming-guides/encoding/"
upstream_commit = "f72a6a648b34e9e098cbce1519bc9c8139105d66"
translated_at = "2026-11-19"
status = "translated"
translator = "agent"
+++

本文介绍 Protobuf 的线路格式（wire format），它定义了消息（message）在线路上的发送细节，以及消息在磁盘上占用的空间。在应用程序中使用 Protobuf 时，你多半不需要了解这些内容，但这些信息对做优化很有帮助。

如果你已经了解这些概念，只是想要一份参考资料，可直接跳到[精简参考卡](#cheat-sheet)一节。

[Protoscope](https://github.com/protocolbuffers/protoscope) 是一种非常简单的语言，用于描述底层线路格式的片段，我们将用它来为各种消息的编码提供直观的参考。Protoscope 的语法由一系列*记号（token）*构成，每个记号都会编码为特定的字节序列。

例如，反引号表示原始十六进制字面量，如 `` `70726f746f6275660a`
``。它会编码为字面量中以十六进制表示的确切字节。引号表示 UTF-8 字符串，如 `"Hello, Protobuf!"`。该字面量等价于 `` `48656c6c6f2c2050726f746f62756621` ``（仔细观察的话，你会发现它由 ASCII 字节组成）。在讨论线路格式的各个方面时，我们会陆续介绍更多 Protoscope 语言的内容。

Protoscope 工具还可以把已编码的 Protobuf 消息转储为文本。示例参见 https://github.com/protocolbuffers/protoscope/tree/main/testdata。

本主题中的所有示例均假定你使用的是版次 2023 或更高版次。

## 一个简单的消息 {#simple}

假设你有下面这个非常简单的消息定义：

```proto
message Test1 {
  int32 a = 1;
}
```

在应用程序中，你创建一个 `Test1` 消息，并把 `a` 设为 150，然后将这条消息序列化（serialization）到输出流。如果你能查看编码后的消息，会看到三个字节：

```proto
08 96 01
```

到目前为止，它就是个很小的纯数字——但它是什么意思呢？如果用 Protoscope 工具转储这些字节，会得到类似 `1: 150` 的输出。它是怎么知道这就是消息内容的？

## Base 128 varint {#varints}

可变宽度整数，也就是 varint（可变长度整数），是线路格式的核心。它允许用 1 到 10 个字节编码无符号 64 位整数，值越小所用字节越少。

varint 中的每个字节都有一个*继续位*（continuation bit），用于指示紧随其后的字节是否仍是这个 varint 的一部分。它就是该字节的最高有效位（most significant bit，即 MSB），有时也称为*符号位*（sign bit）。低 7 位是载荷（payload）；最终的整数由组成它的各字节的 7 位载荷依次拼接而成。

举例来说，数字 1 编码为 `` `01` ``——只有一个字节，因此最高有效位没有置位：

```proto
0000 0001
^ msb
```

再比如 150，编码为 `` `9601` ``——这就稍微复杂一些：

```proto
10010110 00000001
^ msb    ^ msb
```

怎么看出这是 150？首先去掉每个字节的最高有效位——它只是用来标记你是否已经读到这个数字的结尾（如你所见，第一个字节中这一位是置位的，因为这个 varint 有多个字节）。这 7 位载荷按小端序（little-endian）排列。将其转为大端序（big-endian），拼接起来，再按无符号 64 位整数解读：

```proto
10010110 00000001        // 原始输入。
 0010110  0000001        // 去掉继续位。
 0000001  0010110        // 转换为大端序。
   00000010010110        // 拼接。
 128 + 16 + 4 + 2 = 150  // 按无符号 64 位整数解读。
```

由于 varint 对 Protobuf 至关重要，protoscope 语法直接把它们写作普通整数。`150` 与 `` `9601` `` 等价。

## 消息结构 {#structure}

一条 Protobuf 消息就是一系列键值对（key-value pair）。消息的二进制形式只把字段（field）的编号（field number）用作键——每个字段的名称和声明类型只能在解码端参照该消息类型的定义（即 `.proto` 文件）才能确定。Protoscope 拿不到这些信息，因此只能给出字段编号。

消息编码时，每个键值对都会转成一条*记录（record）*，其中包含字段编号、线路类型（wire type）和载荷。线路类型告诉解析器（parser）紧随其后的载荷有多大。这使得旧解析器可以跳过自己不理解的新字段。这类方案有时被称为[标签-长度-值（Tag-Length-Value）](https://en.wikipedia.org/wiki/Type%E2%80%93length%E2%80%93value)，即 TLV。

线路类型共有六种：`VARINT`、`I64`、`LEN`、`SGROUP`、`EGROUP` 和 `I32`

ID  | 名称   | 适用类型
--- | ------ | --------------------------------------------------------
0   | VARINT | int32、int64、uint32、uint64、sint32、sint64、bool、enum
1   | I64    | fixed64、sfixed64、double
2   | LEN    | string、bytes、内嵌消息、packed 的 repeated 字段
3   | SGROUP | 组的开始（已弃用）
4   | EGROUP | 组的结束（已弃用）
5   | I32    | fixed32、sfixed32、float

记录的“标签（tag）”会被编码为一个 varint：由字段编号和线路类型按公式 `(field_number << 3) | wire_type` 组合而成。换句话说，解出表示字段的 varint 后，低 3 位告诉我们线路类型，其余部分告诉我们字段编号。

现在再回头看那个简单示例。你已经知道，字节流中的第一个数字永远是 varint 键，此处的 `` `08` `` 去掉最高有效位后就是：

```proto
000 1000
```

取最后三位得到线路类型（0），再右移三位得到字段编号（1）。Protoscope 将标签表示为一个整数，后跟冒号和线路类型，因此上面的字节可以写作 `1:VARINT`。

由于线路类型为 0（即 `VARINT`），我们知道需要再解码一个 varint 来取得载荷。如前所述，字节 `` `9601` `` 按 varint 解码得到 150，这样就得到了完整的记录。在 Protoscope 中可写作 `1:VARINT 150`。

如果 `:` 后面是空白，Protoscope 就能推断标签的类型。它会向前查看下一个记号，猜测你的意图（具体规则详见 [Protoscope 的 language.txt](https://github.com/protocolbuffers/protoscope/blob/main/language.txt)）。例如在 `1: 150` 中，无类型标签后面紧跟一个 varint，因此 Protoscope 推断其类型为 `VARINT`。如果写 `2: {}`，它会看到 `{` 并猜测为 `LEN`；如果写 `3: 5i32`，它会猜测为 `I32`，依此类推。

## 更多整数类型 {#int-types}

### 布尔值与枚举 {#bools-and-enums}

布尔值和枚举的编码方式与 `int32` 相同。其中布尔值总是编码为 `` `00` `` 或 `` `01` ``。在 Protoscope 中，`false` 和 `true` 就是这两个字节串的别名。

### 有符号整数 {#signed-ints}

正如上一节所述，所有与线路类型 0 相关联的 Protobuf 类型都编码为 varint。但 varint 是无符号的，因此不同的有符号类型——`sint32`、`sint64` 与 `int32`、`int64`——编码负整数的方式并不相同。

`intN` 类型采用二进制补码（two's complement）编码负数，也就是说，把负数看作无符号 64 位整数时，其最高位是置位的。这就意味着*全部十个字节*都必须用上。例如，`-2` 会被 protoscope 转换成：

```proto
11111110 11111111 11111111 11111111 11111111
11111111 11111111 11111111 11111111 00000001
```

这就是 2 的*二进制补码*，在无符号算术中定义为 `~0 - 2 + 1`，其中 `~0` 是全 1 的 64 位整数。弄明白为什么会出现这么多 1，是个不错的练习。

<!-- mdformat off(the asterisks cause bullets) -->
`sintN` 不用二进制补码，而是采用 “ZigZag” 编码来编码负整数。正整数 `p` 编码为 `2 * p`（偶数），负整数 `n` 编码为 `2 * |n| - 1`（奇数）。这样，编码就在正负数之间以 “zigzag”（之字形）方式来回跳变。例如：
<!-- mdformat on -->

原始有符号值 | 编码后
--------------- | ----------
0               | 0
-1              | 1
1               | 2
-2              | 3
...             | ...
0x7fffffff      | 0xfffffffe
-0x80000000     | 0xffffffff

换句话说，对 `sint32` 而言，每个值 `n` 都用下面的公式编码：

```
(n << 1) ^ (n >> 31)
```

64 位版本则用：

```
(n << 1) ^ (n >> 63)
```

`sint32` 或 `sint64` 被解析（parse）时，其值会被解码回原始的有符号值。

在 protoscope 中，给整数加上 `z` 后缀就会让它按 ZigZag 编码。例如，`-500z` 等价于 varint `999`。

### 非 varint 数值类型 {#non-varints}

非 varint 数值类型很简单。`double` 和 `fixed64` 的线路类型为 `I64`，即告诉解析器接下来是固定 8 字节的数据块。`double` 值按 IEEE 754 双精度格式编码。写入 `5: 25.4` 即可指定一条 `double` 记录，写入 `6: 200i64` 则指定一条 `fixed64` 记录。

类似地，`float` 和 `fixed32` 的线路类型为 `I32`，此时解析器应期待 4 个字节。`float` 值按 IEEE 754 单精度格式编码。其语法就是加上 `i32` 后缀：`25.4i32` 会输出 4 个字节，`200i32` 亦然。标签类型会被推断为 `I32`。

## 长度界定记录 {#length-types}

*长度前缀（length prefix）*是线路格式中的另一个重要概念。`LEN` 线路类型的长度是动态的，由紧跟在标签之后的一个 varint 指定，随后照常是载荷。

看看下面这个消息模式（schema）：

```proto
message Test2 {
  string b = 2;
}
```

字段 `b` 的记录是一个字符串，字符串采用 `LEN` 编码。若把 `b` 设为 `"testing"`，就会得到一条字段编号为 2 的 `LEN` 记录，内容为 ASCII 字符串 `"testing"`。结果是 `` `120774657374696e67` ``。把这些字节拆开：

```proto
12 07 [74 65 73 74 69 6e 67]
```

可以看到标签 `` `12` `` 即 `00010 010`，也就是 `2:LEN`。紧随其后的字节是 int32 varint `7`，再往后的七个字节是 `"testing"` 的 UTF-8 编码。int32 varint 意味着字符串的最大长度为 2GB。

在 Protoscope 中写作 `2:LEN 7 "testing"`。不过，重复书写字符串的长度会不太方便（在 Protoscope 文本中，字符串本身已用引号界定）。用花括号包裹 Protoscope 内容会自动生成相应的长度前缀：`{"testing"}` 是 `7 "testing"` 的简写。`{}` 总是被字段推断为 `LEN` 记录，因此这条记录可以简单地写作 `2: {"testing"}`。

`bytes` 字段的编码方式与此相同。

### 子消息 {#embedded}

子消息（submessage）字段同样使用 `LEN` 线路类型。下面是一个消息定义，其中内嵌了我们最初的示例消息 `Test1`：

```proto
message Test3 {
  Test1 c = 3;
}
```

如果 `Test1` 的 `a` 字段（即 `Test3` 的 `c.a` 字段）被设为 150，会得到 `
``1a03089601`` `。拆开来看：

```proto
 1a 03 [08 96 01]
```

最后三个字节（即 `[]` 中的部分）与[最开始的示例](#simple)中的字节完全相同。这些字节前面是一个 `LEN` 类型的标签和长度 3，与字符串的编码方式完全相同。

在 Protoscope 中，子消息的表示相当简洁。` ``1a03089601`` ` 可以写作 `3: {1: 150}`。

## 缺失的元素 {#optional}

缺失的字段很容易编码：字段不存在时直接省略其记录即可。这意味着只设置了少数字段的“庞大” proto 会非常稀疏。

<span id="packed"></span>

## 重复的元素 {#repeated}

从版次 2023 开始，原始类型的 `repeated` 字段（即 `string` 和 `bytes` 之外的所有[标量类型（scalar type）](/programming-guides/proto2#scalar)）默认采用[“紧凑编码（packed）”](/editions/features#repeated_field_encoding)。

packed 的 `repeated` 字段不再为每个元素各编码一条记录，而是编码为单条 `LEN` 记录，其中依次拼接了各个元素。解码时，从 `LEN` 记录中逐个解码元素，直到载荷耗尽为止。下一个元素的起点由前一个元素的长度决定，而该长度又取决于字段的类型。因此，如果我们有：

```proto
message Test4 {
  string d = 4;
  repeated int32 e = 5;
}
```

并构造一个 `Test4` 消息：`d` 设为 `"hello"`，`e` 设为 `1`、`2` 和 `3`，那么它*可以*编码为 `` `220568656c6c6f2a03010203` ``，用 Protoscope 写出来就是：

```proto
4: {"hello"}
5: {1 2 3}
```

不过，如果 repeated 字段被设置为 expanded（覆盖默认的 packed 状态），或者本身不可打包（如字符串和消息），则会为每个值单独编码一条记录。此外，`e` 的各条记录不必连续出现，可以与其他字段交错；只有同一条字段的各条记录之间的相对顺序会得到保留。因此，编码结果也可能如下：

```proto
5: 1
5: 2
4: {"hello"}
5: 3
```

只有原始数值类型的 repeated 字段才能声明为 “packed”。这类类型通常使用 `VARINT`、`I32` 或 `I64` 线路类型。

注意：尽管对 packed 的 repeated 字段来说，通常没有理由把多于一个键值对编码进去，但解析器必须做好接受多个键值对的准备。在这种情况下，各段载荷应拼接在一起，且每个键值对必须包含整数个元素。下面是上述同一条消息的一种有效编码，解析器必须能够接受：

```proto
5: {1 2}
4: {"hello"}
5: {3}
```

Protobuf 解析器必须既能把按 `packed` 编译的 repeated 字段当作未 packed 的来解析，也能反向处理。这样就能以向前兼容和向后兼容的方式为现有字段添加 `[packed=true]`。

### oneof {#oneofs}

[`Oneof` 字段](/programming-guides/proto2#oneof)的编码方式与这些字段不在 `oneof` 中时完全相同。适用于 `oneof` 的规则与其在线路上的表示方式无关。

### 最后写入者生效 {#last-one-wins}

通常，编码后的消息里非 `repeated` 字段绝不应出现多个实例，但解析器仍被要求能处理确实出现多个实例的情况。对数值类型和字符串来说，如果同一字段出现多次，解析器接受它看到的*最后*一个值。对内嵌消息字段来说，解析器会合并同一字段的多个实例，效果如同调用 `Message::MergeFrom` 方法——即后一个实例中的所有单数标量字段会替换前一个实例中的对应字段，单数内嵌消息会被合并，`repeated` 字段会被拼接。这些规则的总体效果是：解析两段已编码消息的拼接，与分别解析这两条消息、然后再合并得到的对象，结果完全相同。也就是说，下面这段代码：

```cpp
MyMessage message;
message.ParseFromString(str1 + str2);
```

等价于下面这段代码：

```cpp
MyMessage message, message2;
message.ParseFromString(str1);
message2.ParseFromString(str2);
message.MergeFrom(message2);
```

这个特性偶尔很有用：即使不知道两条消息的类型，也可以（通过拼接）合并它们。

### 映射 {#maps}

map 字段只是一种特殊 repeated 字段的简写。如果我们有：

```proto
message Test6 {
  map<string, int32> g = 7;
}
```

它实际上等价于：

```proto
message Test6 {
  message g_Entry {
    string key = 1;
    int32 value = 2;
  }
  repeated g_Entry g = 7;
}
```

因此，map 的编码几乎与 `repeated` 消息字段完全一样：表现为一系列 `LEN` 类型的记录，每条记录包含两个字段。唯一的例外是：map 在序列化时不保证保留其顺序。

## 组 {#groups}

组（group）是一种已弃用、不应再使用的特性，但它仍存在于线路格式中，值得简要一提。

组有点类似子消息，但它由特殊标签而非 `LEN` 前缀来界定。消息中的每个组都有一个字段编号，这些特殊标签会用到该编号。

字段编号为 `8` 的组以 `8:SGROUP` 标签开始。`SGROUP` 记录的载荷为空，所以它的作用只是标记组的开始。组内所有字段列完之后，用对应的 `8:EGROUP` 标签标记组的结束。`EGROUP` 记录同样没有载荷，所以 `8:EGROUP` 本身就是完整的记录。组的字段编号必须配对。如果在我们期望 `8:EGROUP` 的地方遇到了 `7:EGROUP`，这条消息就是格式错误的。

Protoscope 为书写组提供了一种便捷语法。与其写成：

```proto
8:SGROUP
  1: 2
  3: {"foo"}
8:EGROUP
```

不如使用 Protoscope 允许的写法：

```proto
8: !{
  1: 2
  3: {"foo"}
}
```

这会生成相应的组开始与组结束标记。`!{}` 语法只能紧跟在无类型标签表达式（如 `8:`）之后使用。

## 字段顺序 {#order}

字段编号在 `.proto` 文件中可以按任意顺序声明。所选顺序对消息的序列化方式没有影响。

消息序列化时，其已知字段和[未知字段（unknown fields）](/programming-guides/proto2#updating)的写入顺序都没有任何保证。序列化顺序属于实现细节，任何特定实现的细节未来都可能变化。因此，Protobuf 解析器必须能够按任意顺序解析字段。

### 影响 {#implications}

*   不要假设消息序列化后的字节输出是稳定的。对于其 bytes 字段中传递性地包含其他已序列化 Protobuf 消息的消息，尤其如此。
*   默认情况下，对同一个 Protobuf 消息实例反复调用序列化方法，得到的字节输出可能并不相同。也就是说，默认的序列化不是确定性的（deterministic）。
    *   确定性序列化只保证在同一个二进制程序内字节输出相同；在不同版本的二进制程序之间，字节输出可能会变化。
*   对 Protobuf 消息实例 `foo` 来说，以下检查可能会失败：
    *   `foo.SerializeAsString() == foo.SerializeAsString()`
    *   `Hash(foo.SerializeAsString()) == Hash(foo.SerializeAsString())`
    *   `CRC(foo.SerializeAsString()) == CRC(foo.SerializeAsString())`
    *   `FingerPrint(foo.SerializeAsString()) ==
        FingerPrint(foo.SerializeAsString())`
*   下面举几个例子，说明逻辑上等价的 Protobuf 消息 `foo` 和 `bar` 可能序列化为不同的字节输出：
    *   `bar` 由旧版服务器序列化，该服务器把某些字段当作未知字段处理。
    *   `bar` 由以另一种编程语言实现的服务器序列化，其字段序列化顺序不同。
    *   `bar` 有一个字段以非确定性的方式序列化。
    *   `bar` 有一个字段存储了某条 Protobuf 消息的序列化字节输出，而那条消息本身被以不同的方式序列化。
    *   `bar` 由新版服务器序列化，该服务器因实现变更而以不同的顺序序列化字段。
    *   `foo` 和 `bar` 是把同一批单独消息按不同顺序拼接而成的结果。

## 编码后 Proto 的大小限制 {#size-limit}

proto 序列化后必须小于 2 GiB。许多 proto 实现会拒绝序列化或解析超过此限制的消息。

## 精简参考卡 {#cheat-sheet}

下面以易于查阅的形式列出线路格式中最主要的内容。

```none
message    := (tag value)*

tag        := (field << 3) bit-or wire_type;
                encoded as uint32 varint
value      := varint      for wire_type == VARINT,
              i32         for wire_type == I32,
              i64         for wire_type == I64,
              len-prefix  for wire_type == LEN,
              <empty>     for wire_type == SGROUP or EGROUP

varint     := int32 | int64 | uint32 | uint64 | bool | enum | sint32 | sint64;
                encoded as varints (sintN are ZigZag-encoded first)
i32        := sfixed32 | fixed32 | float;
                encoded as 4-byte little-endian (float is IEEE 754
                single-precision); memcpy of the equivalent C types (u?int32_t,
                float)
i64        := sfixed64 | fixed64 | double;
                encoded as 8-byte little-endian (double is IEEE 754
                double-precision); memcpy of the equivalent C types (u?int64_t,
                double)

len-prefix := size (message | string | bytes | packed);
                size encoded as int32 varint
string     := valid UTF-8 string (e.g. ASCII);
                max 2GB of bytes
bytes      := any sequence of 8-bit bytes;
                max 2GB of bytes
packed     := varint* | i32* | i64*,
                consecutive values of the type specified in `.proto`
```

另请参阅 [Protoscope 语言参考](https://github.com/protocolbuffers/protoscope/blob/main/language.txt)。

### 图例 {#cheat-sheet-key}

`message   := (tag value)*`
:   一条消息被编码为零个或多个“标签-值”对的序列。

`tag        := (field << 3) bit-or wire_type`
:   标签由两部分组合而成：存于最低三位的 `wire_type`，以及 `.proto` 文件中定义的字段编号。

`value      := varint   for wire_type == VARINT, ...`
:   值的存储方式取决于标签中指定的 `wire_type`。

`varint     := int32 | int64 | uint32 | uint64 | bool | enum | sint32 | sint64`
:   可以使用 varint 来存储上列任意数据类型。

`i32        := sfixed32 | fixed32 | float`
:   可以使用 fixed32 来存储上列任意数据类型。

`i64        := sfixed64 | fixed64 | double`
:   可以使用 fixed64 来存储上列任意数据类型。

`len-prefix := size (message | string | bytes | packed)`
:   带长度前缀的值先存储一个长度（编码为 varint），随后是上列数据类型之一。

`string     := valid UTF-8 string (e.g. ASCII)`
:   如前所述，字符串必须使用 UTF-8 字符编码，且不能超过 2GB。

`bytes      := any sequence of 8-bit bytes`
:   如前所述，bytes 可存储自定义数据类型，最大 2GB。

`packed     := varint* | i32* | i64*`
:   存储协议定义中所述类型的连续值时，使用 `packed` 数据类型。第一个值之后的其余值不再携带标签，从而把标签开销摊薄为每个字段一个，而不是每个元素一个。

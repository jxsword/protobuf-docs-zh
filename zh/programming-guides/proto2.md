+++
title = "语言指南（proto 2）"
weight = 40
description = "介绍如何在你的项目中使用 Protobuf 语言的 proto2 修订版。"
aliases = "/programming-guides/proto/"
type = "docs"
source_url = "https://protobuf.dev/programming-guides/proto2/"
upstream_commit = "f72a6a648b34e9e098cbce1519bc9c8139105d66"
translated_at = "2026-11-19"
status = "translated"
translator = "agent"
+++

本指南介绍如何使用 Protobuf 语言来组织你的 Protobuf 数据，包括 `.proto` 文件语法，以及如何从你的 `.proto` 文件生成数据访问类。它涵盖 Protobuf 语言的 **proto2** 修订版。

有关**版次（editions）**语法的信息，请参阅 [Protobuf 版次语言指南](/programming-guides/editions)。

有关 **proto3** 语法的信息，请参阅 [Proto3 语言指南](/programming-guides/proto3)。

这是一份参考指南——要查看一个使用本文档所述许多特性（feature）的分步示例，请参阅你所选语言的[教程](/getting-started)。

## 定义消息类型 {#simple}

首先我们来看一个非常简单的示例。假设你想定义一个搜索请求消息（message）格式，其中每个搜索请求都包含一个查询字符串、你感兴趣的结果所在的具体页码，以及每页的结果数量。下面就是你用来定义该消息类型的 `.proto` 文件。

```proto
syntax = "proto2";

message SearchRequest {
  optional string query = 1;
  optional int32 page_number = 2;
  optional int32 results_per_page = 3;
}
```

*   文件的第一行指定你使用的是 Protobuf 语言规范的 proto2 修订版。

    *   `syntax` 必须是文件中第一个非空且非注释的行。
    *   如果未指定 `syntax`，Protobuf 编译器将假定你在使用 proto2。

*   `SearchRequest` 消息定义指定了三个字段（field）（名称/值对），每个字段对应你要包含在该类型消息中的一段数据。每个字段都有一个名称和一个类型。

### 指定字段类型 {#specifying-types}

在前面的示例中，所有字段都是[标量类型](#scalar)（scalar）：两个整数（`page_number` 和 `results_per_page`）以及一个字符串（`query`）。你还可以为字段指定[枚举](#enum)（enum）以及其他消息类型等复合类型。

### 分配字段编号 {#assigning}

你必须为消息定义中的每个字段指定一个介于 `1` 到 `536,870,911` 之间的编号，并遵守以下限制：

-   该编号在该消息的所有字段中**必须唯一**。
-   字段编号 `19,000` 到 `19,999` 为 Protobuf 实现保留。如果你在消息中使用了这些保留的字段编号之一，Protobuf 编译器会报错。
-   你不能使用任何先前已[保留](#fieldreserved)的字段编号，也不能使用任何已分配给[扩展](#extensions)的字段编号。

一旦你的消息类型投入使用，该编号就**不能再更改**，因为它在[消息线路格式](/programming-guides/encoding)（wire format）中标识该字段。“更改”字段编号相当于删除该字段，并创建一个类型相同但编号不同的新字段。有关如何正确执行此操作，请参阅[删除字段](#deleting)。

字段编号**绝不应被复用**。绝不要把某个字段编号从[保留](#fieldreserved)列表中取出、用于新的字段定义。请参阅[复用字段编号的后果](#consequences)。

对于最常被赋值的字段，你应当使用 1 到 15 的字段编号。较小的字段编号值在线路格式中占用更少的空间。例如，1 到 15 范围内的字段编号编码（encoding）时占一个字节；16 到 2047 范围内的字段编号占两个字节。你可以在
[Protobuf 编码](/programming-guides/encoding#structure)中了解更多相关信息。

#### 复用字段编号的后果 {#consequences}

复用字段编号会使线路格式消息的解码产生歧义。

Protobuf 线路格式非常精简，它没有提供任何方法来检测“使用某个定义编码、却使用另一个定义解码”的字段。

使用一个定义编码某个字段、再用另一个不同的定义解码同一字段，可能导致：

-   开发者把时间浪费在调试上
-   解析/合并错误（最好的情况）
-   泄露 PII/SPII（个人身份信息/敏感个人身份信息）
-   数据损坏

字段编号复用的常见原因：

-   重新编排字段编号（有时是为了让字段的编号顺序在视觉上更美观）。重新编号实际上相当于把所有涉及重编的字段删除再重新添加，从而导致不兼容的线路格式变更。
-   删除字段时没有[保留](#fieldreserved)其编号，以防止将来被复用。

    -   出于若干原因，在使用[扩展字段](#extensions)时这是一个非常容易犯的错误。
        [扩展声明](/programming-guides/extension_declarations)
        提供了一种保留扩展字段的机制。

字段编号被限制为 29 位而非 32 位，因为有 3 个位用于指定字段的线路格式。欲了解更多，请参阅
[编码主题](/programming-guides/encoding#structure)。

<a id="specifying-rules"></a>

### 指定字段基数 {#field-labels}

消息字段可以是以下几种之一：

*   *单数（singular）*：

    在 proto2 中，单数字段有两种类型：

    *   `optional`：（推荐）`optional` 字段处于以下两种可能状态之一：

        *   字段已设置，包含一个被显式设置或从线路解析而来的值。它会被序列化到线路上。
        *   字段未设置，将返回默认值（default value）。它不会被序列化到线路上。

        你可以检查某个值是否被显式设置过。

    *   `required`：**不要使用。** required 字段的问题非常严重，因此已从 proto3 和版次中移除。required 字段的语义应当在应用层实现。
        当它*确实*被使用时，格式良好（well-formed）的消息必须恰好包含一个该字段。

*   `repeated`：这种字段类型在格式良好的消息中可以重复出现零次或多次。重复值的顺序会被保留。

*   `map`：这是一种键/值对字段类型。有关这种字段类型的更多信息，请参阅
    [映射](/programming-guides/encoding#maps)。

#### 对新的 repeated 字段使用 packed 编码 {#use-packed}

由于历史原因，标量数值类型的 `repeated` 字段（例如 `int32`、`int64`、`enum`）的编码效率没有达到应有的水平。新代码应使用特殊选项 `[packed = true]` 来获得更高效的编码。例如：

```proto
repeated int32 samples = 4 [packed = true];
repeated ProtoEnum results = 5 [packed = true];
```

你可以在
[Protobuf 编码](/programming-guides/encoding#packed)中了解有关 `packed` 编码的更多信息。

#### required 已被强烈弃用 {#required-deprecated}

{{% alert title="Important" color="warning" %}} **required 是永久的**
如前文所述，**新字段不得使用 `required`**。required 字段的语义应当改为在应用层实现。
现有的 `required` 字段应被视为消息定义中永久且不可更改的元素。要把一个字段从
`required` 安全地改成 `optional` 几乎是不可能的。只要可能存在过期的读取方，它就会把
缺少该字段的消息视为不完整，并可能拒绝或丢弃这些消息。 {{% /alert %}}

required 字段的第二个问题出现在有人向枚举添加值的时候。在这种情况下，无法识别的枚举值会被当作缺失处理，这同样会导致 required 值检查失败。

#### 格式良好的消息 {#well-formed}

“格式良好”（well-formed）一词用于 Protobuf 消息时，指的是被序列化/反序列化（serialization/deserialization）的字节。protoc 解析器会验证给定的 proto 定义文件是可解析的。

单数字段在线路格式字节中可能出现不止一次。解析器会接受这样的输入，但只有该字段的最后一个实例可以通过生成的绑定访问。有关此主题的更多信息，请参阅
[最后写入者生效](/programming-guides/encoding#last-one-wins)。

### 添加更多消息类型 {#adding-types}

可以在单个 `.proto` 文件中定义多个消息类型。如果你要定义多个相关的消息，这会很有用——例如，如果你想定义与你的 `SearchResponse` 消息类型相对应的回复消息格式，可以将它添加到同一个 `.proto` 中：

```proto
message SearchRequest {
  optional string query = 1;
  optional int32 page_number = 2;
  optional int32 results_per_page = 3;
}

message SearchResponse {
 ...
}
```

**合并消息会导致膨胀** 虽然多个消息类型（例如消息、枚举和服务）可以在单个 `.proto` 文件中定义，但当在单个文件中定义大量具有不同依赖的消息时，也可能导致依赖膨胀。建议每个 `.proto` 文件中包含尽可能少的消息类型。

### 添加注释 {#adding-comments}

为你的 `.proto` 文件添加注释：

*   优先使用 C/C++/Java 风格的 '//' 行注释，写在 .proto 代码元素的上一行
*   也接受 C 风格的行内/多行注释 `/* ... */`。

    *   使用多行注释时，最好使用带 '*' 的边距行。

```proto
/**
 * SearchRequest 表示一次搜索查询，带有分页选项，
 * 用于指示要在响应中包含哪些结果。
 */
message SearchRequest {
  optional string query = 1;

  // 我们想要哪一页？
  optional int32 page_number = 2;

  // 每页要返回的结果数量。
  optional int32 results_per_page = 3;
}
```

### 删除字段 {#deleting}

如果操作不当，删除字段可能会引发严重问题。

**不要删除** `required` 字段。这几乎不可能安全地做到。如果你必须删除一个 `required` 字段，应当先将该字段标记为 `optional` 和 `deprecated`，并确保所有以任何方式观察该消息的系统都已使用新模式（schema）完成部署。之后你才可以考虑移除该字段（但请注意，这仍然是一个容易出错的过程）。

当你不再需要某个非 `required` 字段时，先从客户端代码中删除对该字段的所有引用，然后再从消息中删除该字段定义。但是，你**必须**[保留被删除字段的编号](#fieldreserved)。如果你不保留该字段编号，开发者在将来就有可能复用它并造成破坏。

你还应当保留字段名，以便消息的 JSON 和 TextFormat 编码能够继续解析。

<a id="fieldreserved"></a>

#### 保留字段编号 {#reserved-field-numbers}

如果你通过完全删除某个字段或将其注释掉来[更新](#updating)消息类型，后续开发者在对该类型进行自己的更新时就可能复用该字段编号。这会造成严重问题，如[复用字段编号的后果](#consequences)所述。为确保这种情况不会发生，请将被删除的字段编号加入 `reserved` 列表。

如果后续开发者试图使用这些保留的字段编号，protoc 编译器会生成错误消息。

```proto
message Foo {
  reserved 2, 15, 9 to 11;
}
```

保留的字段编号范围是闭区间（`9 to 11` 等同于 `9, 10, 11`）。

#### 保留字段名 {#reserved-field-names}

以后复用旧字段名通常是安全的，除非使用 TextProto 或 JSON 这类会序列化字段名的编码。为避免这一风险，你可以把被删除的字段名加入 `reserved` 列表。

保留名称只影响 protoc 编译器的行为，而不影响运行时（runtime）行为，但有一个例外：在解析时，TextProto 实现可能会丢弃名称被保留的未知字段，而不会像对其他未知字段那样报错（目前只有 C++ 和 Go 实现这样做）。运行时的 JSON 解析不受保留名称影响。

```proto
message Foo {
  reserved 2, 15, 9 to 11;
  reserved "foo", "bar";
}
```

注意，不能在同一条 `reserved` 语句中混用字段名和字段编号。

### 从 `.proto` 中会生成什么？ {#generated}

对 `.proto` 运行 [Protobuf 编译器](#generating)时，编译器会用你所选的语言生成处理文件中所描述消息类型所需的生成代码（generated code），包括获取和设置字段值、将消息序列化到输出流，以及从输入流解析消息。

*   对于 **C++**，编译器会从每个 `.proto` 生成一个 `.h` 和一个 `.cc` 文件，其中为你描述的每个消息类型提供一个类。
*   对于 **Java**，编译器会生成一个 `.java` 文件，其中包含每个消息类型的类，以及一个用于创建消息类实例的特殊 `Builder` 类。
*   对于 **Kotlin**，除 Java 生成代码外，编译器还会为每个消息类型生成一个带有改进版 Kotlin API 的 `.kt` 文件。其中包括一个简化消息实例创建的 DSL、一个可空字段访问器（accessor）以及一个复制函数。
*   **Python** 有点不同——Python 编译器会生成一个模块，其中包含你的 `.proto` 中每个消息类型的静态描述符（descriptor），随后该模块会与*元类*（metaclass）配合，在运行时创建所需的 Python 数据访问类。
*   对于 **Go**，编译器会生成一个 `.pb.go` 文件，其中为文件中的每个消息类型提供一个类型。
*   对于 **Ruby**，编译器会生成一个 `.rb` 文件，其中包含一个含有你的消息类型的 Ruby 模块。
*   对于 **Objective-C**，编译器会从每个 `.proto` 生成 `pbobjc.h` 和 `pbobjc.m` 文件，其中为你描述的每个消息类型提供一个类。
*   对于 **C#**，编译器会从每个 `.proto` 生成一个 `.cs` 文件，其中为你描述的每个消息类型提供一个类。
*   对于 **PHP**，编译器会为文件中描述的每个消息类型生成一个 `.php` 消息文件，并为你编译的每个 `.proto` 文件生成一个 `.php` 元数据文件。元数据文件用于将有效的消息类型加载到描述符池（descriptor pool）中。
*   对于 **Dart**，编译器会生成一个 `.pb.dart` 文件，其中为文件中的每个消息类型提供一个类。

你可以按照你所选语言的教程来进一步了解如何使用各语言的 API。更多 API 细节，请参阅相关的 [API 参考](/reference/)。

## 标量值类型 {#scalar}

标量消息字段可以具有以下类型之一——表格展示了 `.proto` 文件中指定的类型，以及自动生成的类中对应的类型：

<div>
  <table>
    <tbody>
      <tr>
        <th>Proto 类型</th>
        <th>说明</th>
      </tr>
      <tr>
        <td>double</td>
        <td></td>
      </tr>
      <tr>
        <td>float</td>
        <td></td>
      </tr>
      <tr>
        <td>int32</td>
        <td>采用可变长度编码。编码负数效率低下——如果你的字段可能出现负值，请改用 sint32。</td>
      </tr>
      <tr>
        <td>int64</td>
        <td>采用可变长度编码。编码负数效率低下——如果你的字段可能出现负值，请改用 sint64。</td>
      </tr>
      <tr>
        <td>uint32</td>
        <td>采用可变长度编码。</td>
      </tr>
      <tr>
        <td>uint64</td>
        <td>采用可变长度编码。</td>
      </tr>
      <tr>
        <td>sint32</td>
        <td>采用可变长度编码。有符号整数值。比常规的 int32 更高效地编码负数。</td>
      </tr>
      <tr>
        <td>sint64</td>
        <td>采用可变长度编码。有符号整数值。比常规的 int64 更高效地编码负数。</td>
      </tr>
      <tr>
        <td>fixed32</td>
        <td>总是四个字节。如果取值经常大于 2<sup>28</sup>，则比 uint32 更高效。</td>
      </tr>
      <tr>
        <td>fixed64</td>
        <td>总是八个字节。如果取值经常大于 2<sup>56</sup>，则比 uint64 更高效。</td>
      </tr>
      <tr>
        <td>sfixed32</td>
        <td>总是四个字节。</td>
      </tr>
      <tr>
        <td>sfixed64</td>
        <td>总是八个字节。</td>
      </tr>
      <tr>
        <td>bool</td>
        <td></td>
      </tr>
      <tr>
        <td>string</td>
        <td>字符串必须始终包含 UTF-8 编码或 7 位 ASCII 文本，长度不能超过 2<sup>32</sup>。</td>
      </tr>
      <tr>
        <td>bytes</td>
        <td>可以包含任意字节序列，长度不超过 2<sup>32</sup>。</td>
      </tr>
    </tbody>
  </table>
</div>

<div>
  <table style="width: 100%;overflow-x: scroll;">
    <tbody>
      <tr>
        <th>Proto 类型</th>
        <th>C++ 类型</th>
        <th>Java/Kotlin 类型<sup>[1]</sup></th>
        <th>Python 类型<sup>[3]</sup></th>
        <th>Go 类型</th>
        <th>Ruby 类型</th>
        <th>C# 类型</th>
        <th>PHP 类型</th>
        <th>Dart 类型</th>
        <th>Rust 类型</th>
      </tr>
      <tr>
        <td>double</td>
        <td>double</td>
        <td>double</td>
        <td>float</td>
        <td>*float64</td>
        <td>Float</td>
        <td>double</td>
        <td>float</td>
        <td>double</td>
        <td>f64</td>
      </tr>
      <tr>
        <td>float</td>
        <td>float</td>
        <td>float</td>
        <td>float</td>
        <td>*float32</td>
        <td>Float</td>
        <td>float</td>
        <td>float</td>
        <td>double</td>
        <td>f32</td>
      </tr>
      <tr>
        <td>int32</td>
        <td>int32_t</td>
        <td>int</td>
        <td>int</td>
        <td>int32</td>
        <td>Fixnum or Bignum (as required)</td>
        <td>int</td>
        <td>integer</td>
        <td>*int32</td>
        <td>i32</td>
      </tr>
      <tr>
        <td>int64</td>
        <td>int64_t</td>
        <td>long</td>
        <td>int/long<sup>[4]</sup></td>
        <td>*int64</td>
        <td>Bignum</td>
        <td>long</td>
        <td>integer/string<sup>[6]</sup></td>
        <td>Int64</td>
        <td>i64</td>
      </tr>
      <tr>
        <td>uint32</td>
        <td>uint32_t</td>
        <td>int<sup>[2]</sup></td>
        <td>int/long<sup>[4]</sup></td>
        <td>*uint32</td>
        <td>Fixnum or Bignum (as required)</td>
        <td>uint</td>
        <td>integer</td>
        <td>int</td>
        <td>u32</td>
      </tr>
      <tr>
        <td>uint64</td>
        <td>uint64_t</td>
        <td>long<sup>[2]</sup></td>
        <td>int/long<sup>[4]</sup></td>
        <td>*uint64</td>
        <td>Bignum</td>
        <td>ulong</td>
        <td>integer/string<sup>[6]</sup></td>
        <td>Int64</td>
        <td>u64</td>
      </tr>
      <tr>
        <td>sint32</td>
        <td>int32_t</td>
        <td>int</td>
        <td>int</td>
        <td>int32</td>
        <td>Fixnum or Bignum (as required)</td>
        <td>int</td>
        <td>integer</td>
        <td>*int32</td>
        <td>i32</td>
      </tr>
      <tr>
        <td>sint64</td>
        <td>int64_t</td>
        <td>long</td>
        <td>int/long<sup>[4]</sup></td>
        <td>*int64</td>
        <td>Bignum</td>
        <td>long</td>
        <td>integer/string<sup>[6]</sup></td>
        <td>Int64</td>
        <td>i64</td>
      </tr>
      <tr>
        <td>fixed32</td>
        <td>uint32_t</td>
        <td>int<sup>[2]</sup></td>
        <td>int/long<sup>[4]</sup></td>
        <td>*uint32</td>
        <td>Fixnum or Bignum (as required)</td>
        <td>uint</td>
        <td>integer</td>
        <td>int</td>
        <td>u32</td>
      </tr>
      <tr>
        <td>fixed64</td>
        <td>uint64_t</td>
        <td>long<sup>[2]</sup></td>
        <td>int/long<sup>[4]</sup></td>
        <td>*uint64</td>
        <td>Bignum</td>
        <td>ulong</td>
        <td>integer/string<sup>[6]</sup></td>
        <td>Int64</td>
        <td>u64</td>
      </tr>
      <tr>
        <td>sfixed32</td>
        <td>int32_t</td>
        <td>int</td>
        <td>int</td>
        <td>*int32</td>
        <td>Fixnum or Bignum (as required)</td>
        <td>int</td>
        <td>integer</td>
        <td>int</td>
        <td>i32</td>
      </tr>
      <tr>
        <td>sfixed64</td>
        <td>int64_t</td>
        <td>long</td>
        <td>int/long<sup>[4]</sup></td>
        <td>*int64</td>
        <td>Bignum</td>
        <td>long</td>
        <td>integer/string<sup>[6]</sup></td>
        <td>Int64</td>
        <td>i64</td>
      </tr>
      <tr>
        <td>bool</td>
        <td>bool</td>
        <td>boolean</td>
        <td>bool</td>
        <td>*bool</td>
        <td>TrueClass/FalseClass</td>
        <td>bool</td>
        <td>boolean</td>
        <td>bool</td>
        <td>bool</td>
      </tr>
      <tr>
        <td>string</td>
        <td>string</td>
        <td>String</td>
        <td>unicode (Python 2), str (Python 3)</td>
        <td>*string</td>
        <td>String (UTF-8)</td>
        <td>string</td>
        <td>string</td>
        <td>String</td>
        <td>ProtoString</td>
      </tr>
      <tr>
        <td>bytes</td>
        <td>string</td>
        <td>ByteString</td>
        <td>bytes</td>
        <td>[]byte</td>
        <td>String (ASCII-8BIT)</td>
        <td>ByteString</td>
        <td>string</td>
        <td>List<int></td>
        <td>ProtoBytes</td>
      </tr>
    </tbody>
  </table>
</div>

<sup>[1]</sup> Kotlin 使用 Java 的对应类型，即使对于无符号类型也是如此，以确保在 Java/Kotlin 混合代码库中的兼容性。

<sup>[2]</sup> 在 Java 中，无符号 32 位和 64 位整数使用对应的有符号类型来表示，最高位直接存储在符号位中。

<sup>[3]</sup> 在所有情况下，为字段设置值时都会执行类型检查，以确保值有效。

<sup>[4]</sup> 64 位或无符号 32 位整数在解码时始终表示为 long，但如果在设置字段时给的是 int，也可以是 int。无论哪种情况，设置的值都必须适合所表示的类型。参见 [2]。

<sup>[5]</sup> proto2 通常从不检查 string 字段的 UTF-8 有效性。不过各语言的行为有所不同，不应在 string 字段中存储无效的 UTF-8 数据。

<sup>[6]</sup> 在 64 位机器上使用 integer，在 32 位机器上使用 string。

你可以在
[Protobuf 编码](/programming-guides/encoding)中进一步了解序列化消息时这些类型是如何编码的。

## 字段默认值 {#default}

解析消息时，如果编码的消息字节中不包含某个特定字段，则在解析后的对象中访问该字段会返回该字段的默认值。默认值因类型而异：

*   对于字符串，默认值是空字符串。
*   对于字节（bytes），默认值是空字节。
*   对于布尔值，默认值是 false。
*   对于数值类型，默认值是零。
*   对于消息字段，该字段未被设置。其具体值取决于所用语言。详情请参阅
    你的语言的[生成代码指南](/reference/)。
*   对于枚举，默认值是**第一个定义的枚举值**，该值应当为 0（为了与开放枚举兼容，推荐这样做）。请参阅[枚举默认值](#enum-default)。

repeated 字段的默认值为空（在相应语言中通常为空列表）。

map 字段的默认值为空（在相应语言中通常为空 map）。

### 覆盖标量默认值 {#explicit-default}

在 proto2 中，你可以为单数非消息字段指定显式默认值。例如，假设你想为 `SearchRequest.results_per_page` 字段提供默认值 10：

```proto
optional int32 results_per_page = 3 [default = 10];
```

如果发送方未指定 `results_per_page`，接收方将观察到以下状态：

*   `results_per_page` 字段不存在。也就是说，`has_results_per_page()`（hazzer 方法）会返回 `false`。
*   `results_per_page` 的值（由“getter”返回）为 `10`。

如果发送方确实发送了 `results_per_page` 的值，则默认值 10 会被忽略，“getter”将返回发送方的值。

有关默认值在生成代码中如何工作的更多细节，请参阅你所选语言的[生成代码指南](/reference/)。

由于枚举的默认值是第一个定义的枚举值，因此在向枚举值列表的开头添加值时要格外小心。有关如何安全更改定义的指导原则，请参阅[更新消息类型](#updating)一节。

## 枚举 {#enum}

定义消息类型时，你可能希望它的某个字段只能取一组预定义值中的一个。例如，假设你想为每个 `SearchRequest` 添加一个 `corpus` 字段，其中语料库（corpus）可以是 `UNIVERSAL`、`WEB`、`IMAGES`、`LOCAL`、`NEWS`、`PRODUCTS` 或 `VIDEO`。你可以非常简单地实现这一点：在消息定义中添加一个 `enum`，并为每个可能的值提供一个常量。

在下面的示例中，我们添加了一个名为 `Corpus` 的 `enum`，其中包含所有可能的值，以及一个 `Corpus` 类型的字段：

```proto
enum Corpus {
  CORPUS_UNSPECIFIED = 0;
  CORPUS_UNIVERSAL = 1;
  CORPUS_WEB = 2;
  CORPUS_IMAGES = 3;
  CORPUS_LOCAL = 4;
  CORPUS_NEWS = 5;
  CORPUS_PRODUCTS = 6;
  CORPUS_VIDEO = 7;
}

message SearchRequest {
  optional string query = 1;
  optional int32 page_number = 2;
  optional int32 results_per_page = 3;
  optional Corpus corpus = 4;
}
```

### 枚举值前缀 {#prefixing-values}

为枚举值添加前缀时，去掉前缀后的名称其余部分仍应是一个合法且符合样式的枚举名。例如，应避免下面这种写法：

```proto
enum DeviceTier {
  DEVICE_TIER_UNKNOWN = 0;
  DEVICE_TIER_1 = 1;
  DEVICE_TIER_2 = 2;
}
```

相反，应使用 `DEVICE_TIER_TIER1` 这样的值名，其中 `DEVICE_TIER_` 部分被视为枚举值的作用域限定，而不是单个枚举值名称的一部分。一些 Protobuf 实现会在安全的前提下自动剥离与所在枚举名称匹配的前缀，但在本例中却无法这样做，因为单独的 `1` 不是合法的枚举值名。

我们计划在未来的版次中增加对带作用域枚举的支持，届时将无需为每个枚举值手动添加前缀，并使其可以简写为 `TIER1 = 1`。

### 枚举默认值 {#enum-default}

`SearchRequest.corpus` 字段的默认值是 `CORPUS_UNSPECIFIED`，因为它是枚举中定义的第一个值。

强烈建议将每个枚举的第一个值定义为 `ENUM_TYPE_NAME_UNSPECIFIED = 0;` 或 `ENUM_TYPE_NAME_UNKNOWN = 0;`。这是由 proto2 处理枚举字段未知值的方式决定的。

还建议这个第一个默认值除“此值未指定”之外不具有任何其他语义。

像 `SearchRequest.corpus` 这样的枚举字段的默认值可以像下面这样显式覆盖：

```
  optional Corpus corpus = 4 [default = CORPUS_UNIVERSAL];
```

### 枚举值别名 {#enum-aliases}

你可以通过为不同的枚举常量分配相同的值来定义别名。为此，你需要将 `allow_alias` 选项设置为 `true`。否则，当发现别名时，Protobuf 编译器会生成警告消息。虽然所有别名值对序列化都有效，但反序列化时只使用第一个值。

```proto
enum EnumAllowingAlias {
  option allow_alias = true;
  EAA_UNSPECIFIED = 0;
  EAA_STARTED = 1;
  EAA_RUNNING = 1;
  EAA_FINISHED = 2;
}

enum EnumNotAllowingAlias {
  ENAA_UNSPECIFIED = 0;
  ENAA_STARTED = 1;
  // ENAA_RUNNING = 1;  // 取消本行注释会导致出现警告消息。
  ENAA_FINISHED = 2;
}
```

枚举常量必须处于 32 位整数的取值范围内。由于 `enum` 值在线路上使用
[可变长度整数（varint）编码](/programming-guides/encoding)，负值的编码效率很低，因此不推荐使用。你可以在消息定义内部定义 `enum`（如前面的示例所示），也可以在外部定义——这些 `enum` 可以在你的 `.proto` 文件中的任何消息定义里复用。你还可以把在一个消息中声明的 `enum` 类型用作另一个消息中某字段的类型，语法为 `_MessageType_._EnumType_`。

对使用 `enum` 的 `.proto` 运行 Protobuf 编译器时，生成的代码在 Java、Kotlin 或 C++ 中会有对应的 `enum`；在 Python 中则是一个特殊的 `EnumDescriptor` 类，用于在运行时生成的类中创建一组带整数值的符号常量。

{{% alert title="Important" color="warning" %}} 生成代码可能受到特定语言对枚举常量数量限制的约束（对某种语言而言为几千个的量级）。请查阅你计划使用的
语言的相关限制。
{{% /alert %}}

{{% alert title="Important" color="warning" %}} 有关枚举应当如何工作、以及它们目前在不同语言中实际如何工作的对比，请参阅
[枚举行为](/programming-guides/enum)。
{{% /alert %}}

移除枚举值对已持久化的 proto 来说是破坏性变更（breaking change）。请不要直接移除某个值，而是用 `reserved` 关键字标记该值，以阻止该枚举值被生成代码；或者保留该值，但使用 `deprecated` 字段选项表明它将在稍后被移除：

```proto
enum PhoneType {
  PHONE_TYPE_UNSPECIFIED = 0;
  PHONE_TYPE_MOBILE = 1;
  PHONE_TYPE_HOME = 2;
  PHONE_TYPE_WORK = 3 [deprecated = true];
  reserved 4,5;
}
```

有关如何在应用程序中使用消息 `enum` 的更多信息，请参阅你所选语言的[生成代码指南](/reference/)。

### 保留值 {#reserved}

如果你通过完全移除某个枚举项或将其注释掉来[更新](#updating)枚举类型，后续用户在对该类型进行自己的更新时就可能复用该数值。如果他们之后加载同一个 `.proto` 的旧实例，这会导致严重问题，包括数据损坏、隐私缺陷等。确保这种情况不会发生的一种方法，是把被删除条目的数值（和/或名称——名称同样可能给 JSON 序列化带来问题）指定为 `reserved`。如果后续用户试图使用这些标识符，Protobuf 编译器会报错。你可以使用 `max` 关键字把保留数值范围指定为一直到最大可能值。

```proto
enum Foo {
  reserved 2, 15, 9 to 11, 40 to max;
  reserved "FOO", "BAR";
}
```

注意，不能在同一条 `reserved` 语句中混用字段名和数值。

## 使用其他消息类型 {#other}

你可以使用其他消息类型作为字段类型。例如，假设你想在每个 `SearchResponse` 消息中包含 `Result` 消息——为此，你可以在同一个 `.proto` 中定义一个 `Result` 消息类型，然后在 `SearchResponse` 中指定一个 `Result` 类型的字段：

```proto
message SearchResponse {
  repeated Result results = 1;
}

message Result {
  optional string url = 1;
  optional string title = 2;
  repeated string snippets = 3;
}
```

### 导入定义 {#importing}

在前面的示例中，`Result` 消息类型与 `SearchResponse` 定义在同一个文件中——如果你想用作字段类型的消息类型已经定义在另一个 `.proto` 文件中，该怎么办？

你可以通过*导入*（import）来使用其他 `.proto` 文件中的定义。要导入另一个 `.proto` 的定义，请在文件顶部添加一条 import 语句：

```proto
import "myproject/other_protos.proto";
```

默认情况下，你只能使用直接导入的 `.proto` 文件中的定义。不过，有时你可能需要把某个 `.proto` 文件移动到新位置。与其直接移动 `.proto` 文件并在一次变更中更新所有调用点，不如在旧位置放置一个占位 `.proto` 文件，使用 `import public` 机制把所有导入转发到新位置。

**请注意，公共导入（public import）功能在 Java、Kotlin、TypeScript、JavaScript 或 GCL 中不可用。**

任何导入了包含 `import public` 语句的 proto 的代码，都可以传递性地依赖 `import public` 依赖。例如：

```proto
// new.proto
// 所有定义都已移到这里
```

```proto
// old.proto
// 这是所有客户端都在导入的 proto 文件。
import public "new.proto";
import "other.proto";
```

```proto
// client.proto
import "old.proto";
// 你使用来自 old.proto 和 new.proto 的定义，但不包括 other.proto
```

协议编译器会在命令行上使用 `-I`/`--proto_path` 标志指定的一组目录中搜索被导入的文件。如果没有给出该标志，它会在调用编译器时所在的目录中查找。一般而言，你应当把 `--proto_path` 标志设置为项目的根目录，并为所有导入使用完全限定名。

### 使用 proto3 消息类型 {#proto3}

可以导入
[proto3](/programming-guides/proto3) 和
[版次 2023](/programming-guides/editions) 的消息类型，
并在你的 proto2 消息中使用它们，反之亦然。但是，proto2 枚举不能直接在 proto3 语法中使用（如果导入的 proto2 消息使用了它们则没有问题）。

## 嵌套类型 {#nested}

你可以在其他消息类型内部定义和使用消息类型，如下例所示——这里 `Result` 消息定义在 `SearchResponse` 消息内部：

```proto
message SearchResponse {
  message Result {
    optional string url = 1;
    optional string title = 2;
    repeated string snippets = 3;
  }
  repeated Result results = 1;
}
```

如果你想在它的父消息类型之外复用该消息类型，可以用 `_Parent_._Type_` 来引用它：

```proto
message SomeOtherMessage {
  optional SearchResponse.Result result = 1;
}
```

你可以把消息嵌套到任意深度。在下面的示例中，请注意两个名为 `Inner` 的嵌套类型完全相互独立，因为它们定义在不同的消息中：

```proto
message Outer {       // 第 0 层
  message MiddleAA {  // 第 1 层
    message Inner {   // 第 2 层
      optional int64 ival = 1;
      optional bool  booly = 2;
    }
  }
  message MiddleBB {  // 第 1 层
    message Inner {   // 第 2 层
      optional int32  ival = 1;
      optional bool   booly = 2;
    }
  }
}
```

### 组 {#groups}

**请注意，组（group）特性已弃用，创建新消息类型时不应使用。请改用嵌套消息类型。**

组是在消息定义中嵌套信息的另一种方式。例如，指定一个包含多个 `Result` 的 `SearchResponse` 的另一种方式如下：

```proto
message SearchResponse {
  repeated group Result = 1 {
    optional string url = 1;
    optional string title = 2;
    repeated string snippets = 3;
  }
}
```

组只是把一个嵌套消息类型和一个字段合并成单个声明。在你的代码中，可以把它当作一个拥有名为 `result` 的 `Result` 类型字段的消息来对待（后一个名称会转换为小写，以免与前一个冲突）。因此，这个示例与前面的 `SearchResponse` 完全等价，只是消息采用了不同的[线路格式](/programming-guides/encoding)。

## 更新消息类型 {#updating}

如果现有的消息类型不再完全满足你的需求——例如，你希望消息格式多出一个字段——但你仍然想使用以旧格式创建的代码，不用担心！使用二进制线路格式时，可以在不破坏任何现有代码的情况下非常简单地更新消息类型。

{{% alert title="Note" color="note" %}} 如果你使用 ProtoJSON 或
[proto 文本格式](/reference/protobuf/textformat-spec)
来存储你的 Protobuf 消息，可以对 proto 定义所做的变更会有所不同。ProtoJSON 线路格式下的安全变更
在[这里](/programming-guides/json#json-wire-safety)描述。
{{% /alert %}}

请查看
[Proto 最佳实践](/best-practices/dos-donts)以及
以下规则：

### 二进制线路不安全变更 {#wire-unsafe-changes}

线路不安全变更是指这样一种模式变更：如果你把使用旧模式序列化的数据交给使用新模式（或相反）的解析器解析，就会出问题。只有当你确信数据的所有序列化器和反序列化器都在使用新模式时，才可以进行线路不安全变更。

*   更改任何现有字段的字段编号都是不安全的。
    *   更改字段编号等同于删除该字段并添加一个类型相同的新字段。如果你想重新编排某个字段的编号，请参阅[删除字段](#deleting)的说明。
*   把字段移入现有的 `oneof` 是不安全的。

### 二进制线路安全变更 {#wire-safe-changes}

线路安全变更是指以这种方式演进模式完全安全、不会带来数据丢失或新的解析失败风险的变更。

请注意，任何线路安全变更对特定语言的应用代码而言都可能是破坏性变更。例如，为既有枚举添加一个值，对任何对该枚举使用穷举 switch 的代码来说都会导致编译失败。因此，Google 可能会避免对公开消息进行其中某些类型的变更：AIP（Google API 改进提案）中包含了对哪些变更在那里可以安全进行的指引。

*   添加新字段是安全的。
    *   如果添加了新字段，使用你的“旧”消息格式的代码所序列化的任何消息仍然可以被你的新生成代码解析。你应当牢记这些元素的[默认值](#default)，以便新代码能够正确地与旧代码生成的消息交互。同样，由新代码创建的消息也可以被旧代码解析：旧的二进制程序在解析时只是忽略新字段。详情请参阅
        [未知字段](#unknowns)一节。
*   移除字段是安全的。
    *   在更新后的消息类型中，不得再次使用同一字段编号。你可以选择改为重命名字段，比如加上 "OBSOLETE_" 前缀，或者将字段编号[保留](#fieldreserved)，这样你的 `.proto` 的后续用户就不会意外复用该编号。
*   为枚举添加更多值是安全的。
*   把单个显式存在性（explicit presence）字段或扩展改为**新** `oneof` 的成员是安全的。
*   把只包含一个字段的 `oneof` 改为显式存在性字段是安全的。
*   把字段改为编号和类型相同的扩展是安全的。

### 二进制线路兼容变更（有条件安全） {#conditionally-safe-changes}

与线路安全变更不同，线路兼容意味着在给定变更前后可以解析同样的数据。不过，在这种形态的变更下，数据的解析可能是有损的。例如，把 int32 改为 int64 是兼容变更，但如果写入了大于 INT32_MAX 的值，按 int32 读取它的客户端就会丢弃该数的高位比特。

只有在你谨慎管理向系统推出的过程时，才可以对模式做兼容变更。例如，你可以把 int32 改为 int64，但要确保在新模式部署到所有端点之前继续只写入合法的 int32 值，之后再开始写入更大的值。

如果你的模式发布到了组织之外，通常不应进行线路兼容变更，因为你无法管理新模式的部署，也就无法知道何时使用不同的取值范围才是安全的。

*   `int32`、`uint32`、`int64`、`uint64` 和 `bool` 都是兼容的。
    *   如果从线路解析出的数值不适合相应类型，其效果与你在 C++ 中把该数值强制转换为该类型相同（例如，一个 64 位数按 int32 读取时会被截断为 32 位）。
*   `sint32` 与 `sint64` 彼此兼容，但与其他整数类型*不*兼容。
    *   如果写入的值在 INT_MIN 到 INT_MAX 之间（含边界），用任一类型解析都会得到相同的值。如果写入的 sint64 值超出该范围并被当作 sint32 解析，varint 会先被截断为 32 位，然后再进行 zigzag 解码（这会导致观察到不同的值）。
*   只要字节是有效的 UTF-8，`string` 与 `bytes` 就是兼容的。
*   如果字节中包含该消息的编码实例，嵌入消息与 `bytes` 是兼容的。
*   `fixed32` 与 `sfixed32` 兼容，`fixed64` 与 `sfixed64` 兼容。
*   对于 `string`、`bytes` 和消息字段，单数与 `repeated` 兼容。
    *   如果输入的是 repeated 字段的序列化数据，期望该字段为单数的客户端会在它是原始类型字段时取最后一个输入值，在它是消息类型字段时合并所有输入元素。注意，这对包括布尔和枚举在内的数值类型通常**并不**安全。数值类型的 repeated 字段默认以
        [紧凑编码（packed）](/programming-guides/encoding#packed)
        格式序列化，在期望单数字段时将无法正确解析。
*   `enum` 与 `int32`、`uint32`、`int64` 和 `uint64` 兼容
    *   需要注意，消息反序列化时客户端代码对它们的处理方式可能不同：例如，无法识别的 proto3 `enum` 值会保留在消息中，但消息反序列化时如何表示它取决于具体语言。
*   在 `map<K, V>` 与对应的 `repeated` 消息字段之间转换是二进制兼容的（消息布局及其他限制请参阅下文的[映射](#maps)）。
    *   不过，这种变更的安全性取决于应用程序：在反序列化并重新序列化消息时，使用 `repeated` 字段定义的客户端会产生语义相同的结果；而使用 `map` 字段定义的客户端可能会重排条目并丢弃具有重复键的条目。

## 未知字段 {#unknowns}

未知字段（unknown fields）是格式良好的 Protobuf 序列化数据中表示解析器无法识别的字段的部分。例如，当旧二进制程序解析由带有新字段的新二进制程序发送的数据时，这些新字段在旧二进制程序中就成为未知字段。

proto2 消息会保留未知字段，并在解析过程中和序列化输出中包含它们。

### 保留未知字段 {#retaining}

某些操作可能导致未知字段丢失。例如，如果你执行以下任一操作，未知字段就会丢失：

*   把 proto 序列化为 JSON。
*   遍历消息中的所有字段来填充一个新消息。

为避免丢失未知字段，请执行以下操作：

*   使用二进制格式；避免使用文本格式（text format）进行数据交换。
*   使用面向消息的 API（如 `CopyFrom()` 和 `MergeFrom()`）来复制数据，而不是逐字段复制

TextFormat 有一点特殊。序列化为 TextFormat 时，未知字段会以字段编号打印出来。但把 TextFormat 数据解析回二进制 proto 时，如果存在使用字段编号的条目，解析就会失败。

## 扩展 {#extensions}

扩展（extension）是定义在其容器消息之外的字段；通常位于与容器消息的 `.proto` 文件分开的另一个 `.proto` 文件中。

### 为什么使用扩展？ {#why-ext}

使用扩展主要有两个原因：

*   容器消息的 `.proto` 文件会拥有更少的导入/依赖。这可以缩短构建时间、打破循环依赖，并以其他方式促进松耦合。扩展非常擅长做到这一点。
*   允许系统以最小的依赖和协调把数据附加到容器消息上。扩展并不是实现这一目标的良好方案，因为字段编号空间有限，而且存在
    [复用字段编号的后果](#consequences)。如果你的用例需要对大量扩展保持极低的协调成本，请考虑改用
    [`Any` 消息类型](/reference/protobuf/google.protobuf#any)。

### 扩展示例 {#ext-example}

我们来看一个扩展示例：

```proto
// 文件 kittens/video_ext.proto

import "kittens/video.proto";
import "media/user_content.proto";

package kittens;

// 此扩展允许在 media.UserContent 消息中保存小猫视频。
extend media.UserContent {
  // Video 是从 kittens/video.proto 导入的消息
  repeated Video kitten_videos = 126;
}
```

注意，定义扩展的文件（`kittens/video_ext.proto`）导入了容器消息所在的文件（`media/user_content.proto`）。

容器消息必须将其字段编号的一个子集保留给扩展使用。

```proto
// 文件 media/user_content.proto

package media;

// 一个用于保存用户所创建内容的容器消息。
message UserContent {
  // 将 verification 设置为 `DECLARATION`，以对此范围内的所有
  // 扩展强制执行扩展声明。
  extensions 100 to 199 [verification = DECLARATION];
}
```

容器消息所在的文件（`media/user_content.proto`）定义了消息 `UserContent`，它将字段编号 [100 到 199] 保留给扩展使用。建议为该范围设置 `verification = DECLARATION`，要求其所有扩展都必须有声明。

添加新扩展（`kittens/video_ext.proto`）时，应当在 `UserContent` 中添加相应的声明，并移除 `verification`。

```
// 一个用于保存用户所创建内容的容器消息。
message UserContent {
  extensions 100 to 199 [
    declaration = {
      number: 126,
      full_name: ".kittens.kitten_videos",
      type: ".kittens.Video",
      repeated: true
    }
  ];
}
```

`UserContent` 声明字段编号 `126` 将由一个 `repeated` 扩展字段使用，该字段的完全限定名为 `.kittens.kitten_videos`，完全限定类型为 `.kittens.Video`。要进一步了解扩展声明，请参阅
[扩展声明](/programming-guides/extension_declarations)。

注意，容器消息所在的文件（`media/user_content.proto`）**不会**导入 kitten_video 扩展定义（`kittens/video_ext.proto`）

扩展字段与具有相同字段编号、类型和基数的标准字段在线路格式编码上没有任何差别。因此，只要字段编号、类型和基数保持不变，把标准字段从其容器中移出成为扩展，或者把扩展字段移入其容器消息成为标准字段，都是安全的。

不过，由于扩展定义在容器消息之外，不会为获取和设置特定扩展字段生成专门的访问器。在我们的示例中，Protobuf 编译器**不会生成** `AddKittenVideos()` 或 `GetKittenVideos()` 访问器。相反，扩展要通过参数化函数来访问，例如：`HasExtension()`、`ClearExtension()`、`GetExtension()`、`MutableExtension()` 和 `AddExtension()`。

在 C++ 中，它大致如下所示：

```cpp
UserContent user_content;
user_content.AddExtension(kittens::kitten_videos, new kittens::Video());
assert(1 == user_content.GetExtensionCount(kittens::kitten_videos));
kittens::Video video = user_content.GetExtension(kittens::kitten_videos, 0);
```

### 定义扩展范围 {#defining-ranges}

如果你是容器消息的所有者，就需要为你的消息的扩展定义一个扩展范围。

分配给扩展字段的编号不能再用于标准字段。

在扩展范围定义之后扩大它是安全的。一个好的默认做法是分配 1000 个相对较小的编号，并使用扩展声明密集填充这一空间：

```proto
message ModernExtendableMessage {
  // 此范围内的所有扩展都应使用扩展声明。
  extensions 1000 to 2000 [verification = DECLARATION];
}
```

在实际扩展之前为扩展声明添加范围时，你应当加上 `verification = DECLARATION`，以强制该新范围使用声明。一旦添加了实际声明，这个占位符就可以移除。

把现有扩展范围拆分为覆盖相同总范围的多个范围是安全的。将旧式消息类型迁移到
[扩展声明](/programming-guides/extension_declarations)时
可能需要这样做。例如，迁移前范围可能定义为：

```proto
message LegacyMessage {
  extensions 1000 to max;
}
```

迁移后（拆分范围）则可以是：

```proto
message LegacyMessage {
  // 曾使用未验证分配方案的旧范围。
  extensions 1000 to 524999999 [verification = UNVERIFIED];
  // 使用扩展声明的当前范围。
  extensions 525000000 to max  [verification = DECLARATION];
}
```

通过提高起始字段编号或降低结束字段编号来移动或收缩扩展范围是不安全的。这些变更可能使现有扩展失效。

对于在你的 proto 的大多数实例中都会被填充的标准字段，优先使用 1 到 15 的字段编号。不建议将这些编号用于扩展。

如果你的编号约定可能涉及具有非常大字段编号的扩展，可以使用 `max` 关键字把扩展范围指定为一直到最大可能字段编号：

```proto
message Foo {
  extensions 1000 to max;
}
```

`max` 为 2<sup>29</sup> - 1，即 536,870,911。对于使用
`message_set_wire_format`（MessageSet，已弃用）的消息，`max` 为
2<sup>31</sup> - 2，即 2,147,483,646；请参阅
[Proto 限制](/programming-guides/proto-limits#field-numbers)。

### 选择扩展编号 {#choosing}

扩展只是可以在其容器消息之外指定的字段。[分配字段编号](#assigning)的所有规则同样适用于扩展字段编号。[复用字段编号的后果](#consequences)同样适用于复用扩展字段编号。

如果容器消息使用了
[扩展声明](/programming-guides/extension_declarations)，选择唯一的扩展字段编号就很简单。定义新扩展时，从容器消息中定义的最高扩展范围内，选择高于所有其他声明的最低字段编号。例如，如果容器消息定义如下：

```proto
message Container {
  // 曾使用未验证分配方案的旧范围
  extensions 1000 to 524999999;
  // 使用扩展声明的当前范围。（最高的扩展范围）
  extensions 525000000 to max  [
    declaration = {
      number: 525000001,
      full_name: ".bar.baz_ext",
      type: ".bar.Baz"
    }
    // 525,000,002 是高于所有其他声明的最低字段编号
  ];
}
```

`Container` 的下一个扩展应当添加一个编号为
`525000002` 的新声明。

#### 未验证的扩展编号分配（不推荐） {#unverified}

容器消息的所有者可以选择放弃扩展声明，而采用自己的未验证扩展编号分配策略。

未验证分配方案使用 Protobuf 生态之外的机制，在所选扩展范围内分配扩展字段编号。一个例子是使用 monorepo 的提交编号。从 Protobuf 编译器的角度看，这种系统是“未验证”的，因为没有办法检查某个扩展是否使用了以正当方式获得的扩展字段编号。

与扩展声明这类经验证的系统相比，未验证系统的好处是无需与容器消息所有者协调即可定义扩展。

未验证系统的缺点是 Protobuf 编译器无法保护参与者免于复用扩展字段编号。

**不建议使用未验证的扩展字段编号分配策略**，因为[复用字段编号的后果](#consequences)会落在该消息的所有扩展者身上（而不仅仅是未遵循建议的开发者）。如果你的用例需要极低的协调成本，请考虑改用
[`Any` 消息](/reference/protobuf/google.protobuf#any)。

未验证的扩展字段编号分配策略仅限于 1 到 524,999,999 的范围。525,000,000 及以上的字段编号只能配合扩展声明使用。

### 指定扩展类型 {#specifying-extension-types}

扩展可以是除 `oneof` 和 `map` 之外的任何字段类型。

### 嵌套扩展（不推荐） {#nested-exts}

你可以在另一个消息的作用域中声明扩展：

```proto
import "common/user_profile.proto";

package puppies;

message Photo {
  extend common.UserProfile {
    optional int32 likes_count = 111;
  }
  ...
}
```

在这种情况下，访问该扩展的 C++ 代码是：

```cpp
UserProfile user_profile;
user_profile.SetExtension(puppies::Photo::likes_count, 42);
```

换句话说，唯一的效果是 `likes_count` 定义在 `puppies.Photo` 的作用域内。

这是一个常见的混淆来源：把 `extend` 块嵌套声明在消息类型内部，*并不*意味着外层类型与被扩展类型之间存在任何关系。特别是，前面的示例*并不*意味着 `Photo` 是 `UserProfile` 的某种子类。它只表示符号 `likes_count` 声明在 `Photo` 的作用域内；它只是一个静态成员。

一种常见模式是把扩展定义在扩展字段类型的作用域内——例如，下面是一个针对 `media.UserContent`、类型为 `puppies.Photo` 的扩展，扩展被定义为 `Photo` 的一部分：

```proto
import "media/user_content.proto";

package puppies;

message Photo {
  extend media.UserContent {
    optional Photo puppy_photo = 127;
  }
  ...
}
```

不过，并不要求带有消息类型的扩展必须定义在该类型内部。你也可以使用标准定义模式：

```proto
import "media/user_content.proto";

package puppies;

message Photo {
  ...
}

// 这里甚至可以位于另一个文件中。
extend media.UserContent {
  optional Photo puppy_photo = 127;
}
```

为避免混淆，**首选这种标准（文件级）语法**。对尚不熟悉扩展的用户来说，嵌套语法常被误认为是子类化。

## Any {#any}

`Any` 消息类型让你可以在没有其 .proto 定义的情况下把消息用作嵌入类型。`Any` 以 `bytes` 的形式包含一个任意序列化后的消息，同时还包含一个 URL，该 URL 充当该消息类型的全局唯一标识符，并可以解析到该类型。要使用 `Any` 类型，你需要
[导入](#other) `google/protobuf/any.proto`。

```proto
import "google/protobuf/any.proto";

message ErrorStatus {
  string message = 1;
  repeated google.protobuf.Any details = 2;
}
```

给定消息类型的默认类型 URL 为
`type.googleapis.com/_packagename_._messagename_`。

不同的语言实现会提供运行时库辅助工具，以类型安全的方式打包和拆包 `Any` 值——例如，在 Java 中，`Any` 类型会有特殊的 `pack()` 和 `unpack()` 访问器；而在 C++ 中则有
`PackFrom()` 和 `UnpackTo()` 方法：

```c++
// 将任意消息类型存储到 Any 中。
NetworkErrorDetails details = ...;
ErrorStatus status;
status.add_details()->PackFrom(details);

// 从 Any 中读取任意消息。
ErrorStatus status = ...;
for (const google::protobuf::Any& detail : status.details()) {
  if (detail.Is<NetworkErrorDetails>()) {
    NetworkErrorDetails network_error;
    detail.UnpackTo(&network_error);
    ... processing network_error ...
  }
}
```

如果你想把所包含的消息限制在少数几种类型，并且要求在向列表添加新类型之前先获得许可，请考虑使用带
[扩展声明](/programming-guides/extension_declarations)
的[扩展](#extensions)而不是 `Any` 消息类型。

## Oneof {#oneof}

如果你有一个包含许多 `optional` 字段、且同一时间至多只有一个字段会被设置的消息，你可以使用 oneof 特性来强制这种行为并节省内存。

oneof 字段类似于 `optional` 字段，不同之处在于一个 oneof 中的所有字段共享内存，且同一时间至多只能设置一个字段。设置 oneof 的任何成员都会自动清除所有其他成员。你可以使用特殊的 `case()` 或 `WhichOneof()` 方法（取决于你所选的语言）来检查 oneof 中哪个值（如果有的话）被设置了。

请注意，*如果设置了多个值，按 proto 中的顺序确定的最后设置的值将覆盖之前所有的值*。

oneof 字段的字段编号在其所在消息内必须唯一。

### 使用 Oneof {#using-oneof}

要在 `.proto` 中定义 oneof，你需要使用 `oneof` 关键字，后跟你的 oneof 名称，在本例中为 `test_oneof`：

```proto
message SampleMessage {
  oneof test_oneof {
     string name = 4;
     SubMessage sub_message = 9;
  }
}
```

然后把你的 oneof 字段添加到 oneof 定义中。你可以添加除 `map` 字段之外的任何类型的字段，但不能使用 `required`、`optional` 或 `repeated` 关键字。如果需要向 oneof 中添加 repeated 字段，可以使用一个包含该 repeated 字段的消息。

在你的生成代码中，oneof 字段与常规 `optional` 字段拥有相同的 getter 和 setter。你还会得到一个特殊方法，用于检查 oneof 中哪个值（如果有的话）被设置了。有关你所选语言的 oneof API 的更多信息，请参阅相关的 [API 参考](/reference/)。

### Oneof 特性 {#oneof-features}

*   设置一个 oneof 字段会自动清除 oneof 的所有其他成员。因此，如果你设置了多个 oneof 字段，只有你*最后*设置的字段仍然保有值。

    ```c++
    SampleMessage message;
    message.set_name("name");
    CHECK(message.has_name());
    // 调用 mutable_sub_message() 会清除 name 字段，并将
    // sub_message 设置为一个未设置任何字段的 SubMessage 新实例。
    message.mutable_sub_message();
    CHECK(!message.has_name());
    ```

*   如果解析器在线路上遇到同一个 oneof 的多个成员，解析后的消息只会使用最后看到的那个成员。解析线路上的数据时，从字节的开头开始，读取下一个值，并应用以下解析规则：

    *   首先，检查同一个 oneof 中是否有*另一个*字段当前已被设置，如果有则清除它。

    *   然后像该字段不在 oneof 中那样应用其内容：

        *   原始类型字段会覆盖任何已设置的值
        *   消息类型字段会合并到任何已设置的值中

*   oneof 不支持扩展。

*   oneof 不能是 `repeated` 的。

*   反射（reflection）API 适用于 oneof 字段。

*   如果你把某个 oneof 字段设置为默认值（例如把 int32 类型的 oneof 字段设为 0），该 oneof 字段的“case”会被设置，并且该值会被序列化到线路上。

*   如果你使用 C++，请确保你的代码不会造成内存崩溃。下面的示例代码会崩溃，因为 `sub_message` 已在调用 `set_name()` 方法时被删除。

    ```c++
    SampleMessage message;
    SubMessage* sub_message = message.mutable_sub_message();
    message.set_name("name");      // 将删除 sub_message
    sub_message->set_...            // 这里会崩溃
    ```

*   再说 C++：如果你 `Swap()` 两个带有 oneof 的消息，每个消息最终都会持有对方的 oneof case：在下面的示例中，`msg1` 将拥有
    `sub_message`，而 `msg2` 将拥有 `name`。

    ```c++
    SampleMessage msg1;
    msg1.set_name("name");
    SampleMessage msg2;
    msg2.mutable_sub_message();
    msg1.swap(&msg2);
    CHECK(msg1.has_sub_message());
    CHECK(msg2.has_name());
    ```

### 向后兼容性问题 {#backward}

添加或移除 oneof 字段时要小心。如果检查 oneof 的值返回 `None`/`NOT_SET`，这可能意味着该 oneof 尚未被设置，或者它已被设置为 oneof 另一个版本中的字段。无法区分这两种情况，因为没有办法知道线路上的未知字段是否是 oneof 的成员。

#### 标签复用问题 {#reuse}

*   **把 `optional` 字段移入或移出 oneof**：消息经过序列化和解析后，你可能丢失部分信息（某些字段会被清除）。不过，把单个字段移入**新** oneof 是安全的；如果已知同一时间只会设置一个字段，则或许可以移动多个字段。更多细节请参阅[更新消息类型](#updating)。
*   **删除一个 oneof 字段后又把它加回来**：消息经过序列化和解析后，这可能会清除你当前设置的 oneof 字段。
*   **拆分或合并 oneof**：这与移动 `optional` 字段存在类似问题。

## 映射 {#maps}

如果你想在数据定义中创建关联映射，Protobuf 提供了一种便捷的简写语法：

```proto
map<key_type, value_type> map_field = N;
```

其中 `key_type` 可以是任何整数或字符串类型（即除浮点类型和 `bytes` 之外的任何
[标量](#scalar)类型）。注意，枚举和 proto 消息都不能用作 `key_type`。
`value_type` 可以是除另一个映射之外的任何类型。

例如，如果你想创建一个项目映射，其中每个 `Project` 消息都与一个字符串键相关联，可以这样定义：

```proto
map<string, Project> projects = 3;
```

### 映射特性 {#maps-features}

*   映射不支持扩展。
*   映射不能是 `repeated`、`optional` 或 `required` 的。
*   映射值的线路格式顺序和映射迭代顺序都是未定义的，因此你不能依赖映射条目保持某种特定顺序。
*   为 `.proto` 生成文本格式时，映射会按键排序。数值键按数值大小排序。
*   从线路解析或合并时，如果存在重复的映射键，会使用最后看到的键。从文本格式解析映射时，如果存在重复键，解析可能会失败。
*   如果你为映射字段提供了键但没有提供值，该字段被序列化时的行为取决于具体语言。在 C++、Java、Kotlin 和 Python 中会序列化该类型的默认值，而在其他语言中则不会序列化任何内容。
*   在与映射 `foo` 相同的作用域中不能存在名为 `FooEntry` 的符号，因为
    `FooEntry` 已被映射的实现所使用。

生成的映射 API 目前已覆盖所有受支持的语言。有关你所选语言的映射 API 的更多信息，请参阅相关的
[API 参考](/reference/)。

### 向后兼容 {#backwards}

映射语法在线路上等价于下面的定义，因此不支持映射的 Protobuf 实现仍然可以处理你的数据：

```proto
message MapFieldEntry {
  optional key_type key = 1;
  optional value_type value = 2;
}

repeated MapFieldEntry map_field = N;
```

任何支持映射的 Protobuf 实现都必须既能够生成、也能够接受前述定义所能接受的数据。

## 包 {#packages}

你可以在 `.proto` 文件中添加一个可选的 `package` 声明符，以防止协议消息类型之间发生名称冲突。

```proto
package foo.bar;
message Open { ... }
```

然后你可以在定义消息类型的字段时使用该 package 声明符：

```proto
message Foo {
  ...
  optional foo.bar.Open open = 1;
  ...
}
```

package 声明符影响生成代码的方式取决于你所选的语言：

*   在 **C++** 中，生成的类被包裹在 C++ 命名空间（namespace）中。例如，`Open` 会位于命名空间 `foo::bar` 中。
*   在 **Java** 和 **Kotlin** 中，该 package 会被用作 Java 包，除非你在 `.proto` 文件中显式提供了 `option java_package`。
*   在 **Python** 中，`package` 指令会被忽略，因为 Python 模块是按照其在文件系统中的位置来组织的。
*   在 **Go** 中，`package` 指令会被忽略，生成的 `.pb.go` 文件位于以对应 `go_proto_library`
    Bazel 规则命名的包中。对于开源项目，你**必须**提供 `go_package` 选项或设置 Bazel 的 `-M` 标志。
*   在 **Ruby** 中，生成的类被包裹在嵌套的 Ruby 命名空间中，并转换为 Ruby 要求的大写风格（首字母大写；如果第一个字符不是字母，则加上
    `PB_` 前缀）。例如，`Open` 会位于命名空间 `Foo::Bar` 中。
*   在 **PHP** 中，该 package 会在转换为 PascalCase 后用作命名空间，除非你在 `.proto` 文件中显式提供了 `option php_namespace`。例如，`Open` 会位于命名空间 `Foo\Bar` 中。
*   在 **C#** 中，该 package 会在转换为 PascalCase 后用作命名空间，除非你在 `.proto` 文件中显式提供了 `option csharp_namespace`。例如，`Open` 会位于命名空间 `Foo.Bar` 中。

请注意，即使 `package` 指令不会直接影响生成代码（例如在 Python 中），仍然强烈建议为 `.proto` 文件指定 package，否则可能导致描述符中的命名冲突，并使该 proto 无法移植到其他语言。

### 包与名称解析 {#name-resolution}

Protobuf 语言中的类型名称解析方式与 C++ 类似：先搜索最内层作用域，然后是次内层，依此类推，每个包都被视为其父包的“内层”。前导的 '.'（例如
`.foo.bar.Baz`）则表示从最外层作用域开始。

Protobuf 编译器通过解析被导入的 `.proto` 文件来解析所有类型名称。每种语言的代码生成器（code generator）都知道如何在该语言中引用每个类型，即使该语言有不同的作用域规则。

## 定义服务 {#services}

如果你想把消息类型与远程过程调用（RPC）系统一起使用，可以在 `.proto` 文件中定义一个 RPC 服务接口，Protobuf 编译器会用你所选的语言生成服务接口代码和存根（stub）。例如，如果你想定义一个 RPC 服务，其方法接收你的 `SearchRequest` 并返回 `SearchResponse`，可以在 `.proto` 文件中如下定义：

```proto
service SearchService {
  rpc Search(SearchRequest) returns (SearchResponse);
}
```

默认情况下，协议编译器随后会生成一个名为 `SearchService` 的抽象接口和一个对应的“存根”实现。存根将所有调用转发给一个 `RpcChannel`，而 `RpcChannel` 本身也是一个抽象接口，你需要基于自己的 RPC 系统自行定义。例如，你可以实现一个将消息序列化并通过 HTTP 发送到服务器的 `RpcChannel`。换言之，生成的存根为发起基于 protocol buffer 的 RPC 调用提供了类型安全的接口，同时不会把你锁定在任何特定的 RPC 实现上。因此，在 C++ 中你最终可能会得到类似这样的代码：

```c++
using google::protobuf;

protobuf::RpcChannel* channel;
protobuf::RpcController* controller;
SearchService* service;
SearchRequest request;
SearchResponse response;

void DoSearch() {
  // 你需要提供 MyRpcChannel 和 MyRpcController 类，它们实现了
  // 抽象接口 protobuf::RpcChannel 和 protobuf::RpcController。
  channel = new MyRpcChannel("somehost.example.com:1234");
  controller = new MyRpcController;

  // 协议编译器根据前面给出的定义生成 SearchService 类。
  service = new SearchService::Stub(channel);

  // 设置请求。
  request.set_query("protocol buffers");

  // 执行 RPC。
  service->Search(controller, &request, &response,
                  protobuf::NewCallback(&Done));
}

void Done() {
  delete service;
  delete channel;
  delete controller;
}
```

所有服务类还实现了 `Service` 接口，它提供了一种在编译期不知道方法名及其输入和输出类型的情况下调用特定方法的方式。在服务器端，可以用它来实现一个可注册服务的 RPC 服务器。

```c++
using google::protobuf;

class ExampleSearchService : public SearchService {
 public:
  void Search(protobuf::RpcController* controller,
              const SearchRequest* request,
              SearchResponse* response,
              protobuf::Closure* done) {
    if (request->query() == "google") {
      response->add_result()->set_url("http://www.google.com");
    } else if (request->query() == "protocol buffers") {
      response->add_result()->set_url("http://protobuf.googlecode.com");
    }
    done->Run();
  }
};

int main() {
  // 你需要提供 MyRpcServer 类。它不必实现任何
  // 特定接口；这里只是一个示例。
  MyRpcServer server;

  protobuf::Service* service = new ExampleSearchService;
  server.ExportOnPort(1234, service);
  server.Run();

  delete service;
  return 0;
}
```

如果你不想接入自己现有的 RPC 系统，可以使用
[gRPC](https://github.com/grpc/grpc-common)：这是 Google 开发的一种语言无关、平台无关的开源 RPC 系统。gRPC 与 Protobuf 配合得尤其好，它让你可以使用一个特殊的 Protobuf 编译器插件直接从你的 `.proto` 文件生成相关的 RPC 代码。但是，由于 proto2 与 proto3 生成的客户端和服务器之间可能存在兼容性问题，我们建议你使用 proto3 或版次 2023 来定义 gRPC 服务。你可以在
[Proto3 语言指南](/programming-guides/proto3)中进一步了解 proto3 语法，在
[版次 2023 语言指南](/programming-guides/editions)中了解版次 2023。

除 gRPC 之外，还有许多正在进行的第三方项目在为 Protobuf 开发 RPC 实现。有关我们所知项目链接的列表，请参阅
[第三方附加组件 wiki 页面](https://github.com/protocolbuffers/protobuf/blob/master/docs/third_party.md)。

## JSON 映射 {#json}

标准 Protobuf 二进制线路格式是两个使用 Protobuf 的系统之间通信的首选序列化格式。对于与使用 JSON 而非 Protobuf 线路格式的系统通信，Protobuf 在
[JSON](/programming-guides/json) 中支持一种规范化（canonical）编码。

## 选项 {#options}

`.proto` 文件中的各个声明可以用多个*选项*（option）来注解。选项不会改变声明的整体含义，但可能影响它在特定上下文中的处理方式。可用选项的完整列表定义在 [`/google/protobuf/descriptor.proto`](https://github.com/protocolbuffers/protobuf/blob/main/src/google/protobuf/descriptor.proto) 中。

有些选项是文件级选项，意味着它们应当写在顶层作用域中，而不是任何消息、枚举或服务定义内部。有些选项是消息级选项，意味着它们应当写在消息定义内部。有些选项是字段级选项，意味着它们应当写在字段定义内部。选项还可以写在枚举类型、枚举值、oneof 字段、服务类型和服务方法上；不过，目前这些都还没有任何有用的选项。

以下是一些最常用的选项：

*   `java_package`（文件选项）：你希望生成的 Java/Kotlin 类使用的包。如果 `.proto` 文件中没有显式给出
    `java_package` 选项，则默认使用 proto 包（通过 `.proto` 文件中的
    “package”关键字指定）。不过，proto 包通常不适合直接用作 Java 包，因为 proto 包一般不会以反向域名开头。如果不生成 Java 或 Kotlin 代码，该选项没有效果。

    ```proto
    option java_package = "com.example.foo";
    ```

*   `java_outer_classname`（文件选项）：你想要生成的包装 Java 类的类名（也因此是文件名）。如果 `.proto` 文件中没有显式指定
    `java_outer_classname`，类名将通过把 `.proto` 文件名转换为驼峰式（camel-case）来构造（因此
    `foo_bar.proto` 会变成 `FooBar.java`）。如果 `java_multiple_files` 选项被禁用，那么为该 `.proto`
    文件生成的所有其他类/枚举等都会作为嵌套类/枚举等生成*在这个外层包装 Java 类之内*。如果不生成 Java 代码，该选项没有效果。

    ```proto
    option java_outer_classname = "Ponycopter";
    ```

*   `java_multiple_files`（文件选项）：如果为 false，该 `.proto` 文件只会生成一个 `.java` 文件，为顶层消息、服务和枚举生成的所有 Java
    类/枚举等都会嵌套在一个外层类中（参见
    `java_outer_classname`）。如果为 true，将为顶层消息、服务和枚举生成的每个 Java 类/枚举等分别生成单独的 `.java` 文件，并且为该 `.proto` 文件生成的包装 Java 类不会再包含任何嵌套类/枚举等。这是一个布尔选项，默认值为
    `false`。如果不生成 Java 代码，该选项没有效果。

    ```proto
    option java_multiple_files = true;
    ```

*   `optimize_for`（文件选项）：可以设置为 `SPEED`、`CODE_SIZE` 或
    `LITE_RUNTIME`。它以下列方式影响 C++ 和 Java 代码生成器（也可能影响第三方生成器）：

    *   `SPEED`（默认）：Protobuf 编译器会生成用于序列化、解析以及对消息类型执行其他常见操作的代码。这些代码经过了高度优化。
    *   `CODE_SIZE`：Protobuf 编译器会生成最小化的类，并依赖共享的、基于反射的代码来实现序列化、解析和各种其他操作。因此，生成的代码会比 `SPEED` 模式小得多，但操作速度更慢。类仍然会实现与 `SPEED` 模式下完全相同的公共 API。这种模式最适合包含大量 `.proto` 文件、又不需要所有文件都拥有极致性能的应用。
    *   `LITE_RUNTIME`：Protobuf 编译器会生成只依赖“lite”运行时库（`libprotobuf-lite` 而非
        `libprotobuf`）的类。lite 运行时比完整库小得多（大约小一个数量级），但省略了某些特性，如描述符和反射。这对于运行在手机等受限平台上的应用特别有用。编译器仍会像 `SPEED` 模式那样生成所有方法的快速实现。
        生成的类只会实现各语言中的 `MessageLite` 接口，它只提供完整
        `Message` 接口方法的一个子集。

    ```proto
    option optimize_for = CODE_SIZE;
    ```

*   **通用服务已弃用。**`cc_generic_services`、
    `java_generic_services`、`py_generic_services`（文件选项）：如果为 true，C++、Java 或 Python 代码生成器会基于[服务定义](#services)生成已弃用的抽象服务代码。该功能自 2.3.0 版（2010 年 1 月）起已弃用，默认处于禁用状态。RPC
    实现应当提供
    [代码生成器插件](/reference/cpp/api-docs/google.protobuf.compiler.plugin.pb)
    来生成针对其系统的特定代码，而不是依赖最终会被移除的“抽象”服务。有关弃用背后的原因，请参阅
    [关于通用服务的设计决策](/design-decisions/insertion-points-and-generic-services#generic-services)。

*   `cc_enable_arenas`（文件选项）：为 C++
    生成代码启用 [arena 内存分配](/reference/cpp/arenas)。

*   `objc_class_prefix`（文件选项）：设置 Objective-C 类前缀，该前缀会被加在这个 .proto 生成的所有 Objective-C 类和枚举之前。没有默认值。你应当使用 3 到 5 个大写字符组成的前缀，如
    [Apple 的建议](https://developer.apple.com/library/ios/documentation/Cocoa/Conceptual/ProgrammingWithObjectiveC/Conventions/Conventions.html#//apple_ref/doc/uid/TP40011210-CH10-SW4)。
    注意，所有 2 个字母的前缀都由 Apple 保留。

*   `message_set_wire_format`（消息选项）：如果设置为 `true`，该消息会使用一种不同的二进制格式，旨在与 Google 内部使用的一种名为 `MessageSet` 的旧格式兼容。Google 之外的用户可能永远不需要使用该选项。消息必须严格按如下方式声明：

    ```proto
    message Foo {
      option message_set_wire_format = true;
      extensions 4 to max;
    }
    ```

*   `packed`（字段选项）：在基本数值类型的 repeated 字段上设置为 `true` 时，它会使系统采用一种更紧凑的
    [编码](/programming-guides/encoding#packed)。不使用该选项的唯一原因，是你需要与 2.3.0 版之前的解析器保持兼容。这些旧解析器会在未预期到 packed 数据时将其忽略。因此，在不破坏线路兼容性的前提下，无法把现有字段改为 packed 格式。在 2.3.0 及更高版本中，这一变更是安全的，因为可打包字段的解析器总是同时接受两种格式；但如果你必须应付使用旧版 Protobuf 的旧程序，就要当心。

    ```proto
    repeated int32 samples = 4 [packed = true];
    ```

*   `deprecated`（字段选项）：如果设置为 `true`，表示该字段已弃用（deprecated），新代码不应使用它。在大多数语言中这没有实际效果。在 Java 中，它会变成一个 `@Deprecated` 注解。对于 C++，
    clang-tidy 会在使用弃用字段时生成警告。将来，其他语言的代码生成器也可能在该字段的访问器上生成弃用注解，进而在编译试图使用该字段的代码时引发警告。如果该字段已无人使用、而你想阻止新用户使用它，可以考虑用一条 [reserved](#fieldreserved)
    语句替换该字段声明。

    ```proto
    optional int32 old_field = 6 [deprecated = true];
    ```

### 枚举值选项 {#enum-value-options}

支持枚举值选项。你可以使用 `deprecated` 选项来表示某个值不应再被使用。你还可以使用扩展创建自定义选项。

下面的示例展示了添加这些选项的语法：

```proto
import "google/protobuf/descriptor.proto";

extend google.protobuf.EnumValueOptions {
  optional string string_name = 123456789;
}

enum Data {
  DATA_UNSPECIFIED = 0;
  DATA_SEARCH = 1 [deprecated = true];
  DATA_DISPLAY = 2 [
    (string_name) = "display_value"
  ];
}
```

读取 `string_name` 选项的 C++ 代码可能如下所示：

```cpp
const absl::string_view foo = proto2::GetEnumDescriptor<Data>()
    ->FindValueByName("DATA_DISPLAY")->options().GetExtension(string_name);
```

请参阅[自定义选项](#customoptions)，了解如何将自定义选项应用于枚举值和字段。

### 自定义选项 {#customoptions}

Protobuf 还允许你定义并使用自己的选项。请注意，这是一个大多数人都不需要的**高级特性**。由于选项是由 `google/protobuf/descriptor.proto` 中定义的消息（如
`FileOptions` 或 `FieldOptions`）定义的，定义你自己的选项无非就是[扩展](#extensions)这些消息。例如：

```proto
import "google/protobuf/descriptor.proto";

extend google.protobuf.MessageOptions {
  optional string my_option = 51234;
}

message MyMessage {
  option (my_option) = "Hello world!";
}
```

这里我们通过扩展 `MessageOptions` 定义了一个新的消息级选项。之后在使用该选项时，选项名必须用括号括起来，以表明它是一个扩展。现在我们可以在 C++ 中像下面这样读取 `my_option` 的值：

```proto
string value = MyMessage::descriptor()->options().GetExtension(my_option);
```

这里，`MyMessage::descriptor()->options()` 返回 `MyMessage` 的 `MessageOptions` 协议消息。从中读取自定义选项就像读取任何其他[扩展](#extensions)一样。

同样，在 Java 中我们会这样写：

```java
String value = MyProtoFile.MyMessage.getDescriptor().getOptions()
  .getExtension(MyProtoFile.myOption);
```

在 Python 中则是：

```python
value = my_proto_file_pb2.MyMessage.DESCRIPTOR.GetOptions()
  .Extensions[my_proto_file_pb2.my_option]
```

Protobuf 语言中的每一种构造都可以定义自定义选项。下面是一个用到所有种类选项的示例：

```proto
import "google/protobuf/descriptor.proto";

extend google.protobuf.FileOptions {
  optional string my_file_option = 50000;
}
extend google.protobuf.MessageOptions {
  optional int32 my_message_option = 50001;
}
extend google.protobuf.FieldOptions {
  optional float my_field_option = 50002;
}
extend google.protobuf.OneofOptions {
  optional int64 my_oneof_option = 50003;
}
extend google.protobuf.EnumOptions {
  optional bool my_enum_option = 50004;
}
extend google.protobuf.EnumValueOptions {
  optional uint32 my_enum_value_option = 50005;
}
extend google.protobuf.ServiceOptions {
  optional MyEnum my_service_option = 50006;
}
extend google.protobuf.MethodOptions {
  optional MyMessage my_method_option = 50007;
}

option (my_file_option) = "Hello world!";

message MyMessage {
  option (my_message_option) = 1234;

  optional int32 foo = 1 [(my_field_option) = 4.5];
  optional string bar = 2;
  oneof qux {
    option (my_oneof_option) = 42;

    string quux = 3;
  }
}

enum MyEnum {
  option (my_enum_option) = true;

  FOO = 1 [(my_enum_value_option) = 321];
  BAR = 2;
}

message RequestType {}
message ResponseType {}

service MyService {
  option (my_service_option) = FOO;

  rpc MyMethod(RequestType) returns(ResponseType) {
    // 注意：my_method_option 的类型是 MyMessage。我们可以使用单独的
    //   “option” 行来设置其中的每个字段。
    option (my_method_option).foo = 567;
    option (my_method_option).bar = "Some string";
  }
}
```

请注意，如果想在定义自定义选项的包之外的其他包中使用它，必须在选项名前加上包名，就像类型名一样。例如：

```proto
// foo.proto
import "google/protobuf/descriptor.proto";
package foo;
extend google.protobuf.MessageOptions {
  optional string my_option = 51234;
}
```

```proto
// bar.proto
import "foo.proto";
package bar;
message MyMessage {
  option (foo.my_option) = "Hello world!";
}
```

最后一点：由于自定义选项是扩展，它们必须像其他任何字段或扩展一样被分配字段编号。在前面的示例中，我们使用了 50000-99999 范围内的字段编号。该范围保留给各组织内部使用，因此你可以在内部应用中自由使用该范围内的编号。但是，如果你打算在公开应用中使用自定义选项，那么确保你的字段编号全局唯一就很重要。要获得全局唯一的字段编号，请发送请求在
[Protobuf 全局扩展注册表](https://github.com/protocolbuffers/protobuf/blob/master/docs/options.md)中添加一个条目。通常你只需要一个扩展编号。把多个选项放入一个子消息中，就可以只用一个扩展编号来声明它们：

```proto
message FooOptions {
  optional int32 opt1 = 1;
  optional string opt2 = 2;
}

extend google.protobuf.FieldOptions {
  optional FooOptions foo_options = 1234;
}

// 用法：
message Bar {
  optional int32 a = 1 [(foo_options).opt1 = 123, (foo_options).opt2 = "baz"];
  // 另一种聚合语法（使用 TextFormat）：
  optional int32 b = 2 [(foo_options) = { opt1: 123 opt2: "baz" }];
}
```

另外请注意，每种选项类型（文件级、消息级、字段级等）都有自己独立的编号空间，因此举例来说，你可以为 FieldOptions 和 MessageOptions 的扩展声明相同的编号。

### 选项保留 {#option-retention}

选项有一个*保留性*（retention）概念，用于控制选项是否保留在生成代码中。选项默认具有*运行时保留性*（runtime retention），这意味着它们会保留在生成代码中，因而在运行时可以在生成的描述符池中看到。不过，你可以设置 `retention =
RETENTION_SOURCE` 来指定某个选项（或选项内的字段）不得在运行时保留。这称为*源码保留性*（source retention）。

选项保留性是一个大多数用户无需担心的高级特性，但如果你希望使用某些选项而又不想在二进制文件中付出保留它们的代码体积代价，它就很有用。具有源码保留性的选项对 `protoc` 和 `protoc` 插件仍然可见，因此代码生成器可以利用它们来自定义自己的行为。

保留性可以直接设置在选项上，如下所示：

```proto
extend google.protobuf.FileOptions {
  optional int32 source_retention_option = 1234
      [retention = RETENTION_SOURCE];
}
```

它也可以设置在普通字段上，此时仅当该字段出现在选项内部时才生效：

```proto
message OptionsMessage {
  optional int32 source_retention_field = 1 [retention = RETENTION_SOURCE];
}
```

你也可以随意设置 `retention = RETENTION_RUNTIME`，但由于这是默认行为，这样做没有任何效果。当某个消息字段被标记为
`RETENTION_SOURCE` 时，它的全部内容都会被丢弃；其内部的字段无法通过尝试设置
`RETENTION_RUNTIME` 来推翻这一点。

{{% alert title="Note" color="note" %}} 自 Protobuf 22.0 起，对选项保留性的支持仍在推进中，目前仅支持 C++
和 Java。Go 从 1.29.0 开始支持。Python 的支持已完成，
但尚未进入发布版本。{{% /alert %}}

### 选项目标 {#option-targets}

字段有一个 `targets` 选项，用于控制该字段作为选项使用时可以应用到哪些实体类型。例如，如果某个字段设置了
`targets = TARGET_TYPE_MESSAGE`，那么该字段就不能设置在枚举（或任何其他非消息实体）的自定义选项上。protoc 会强制执行这一点，如果违反目标约束就会报错。

初看之下，这个特性似乎没有必要，因为每个自定义选项都是针对特定实体的选项消息的扩展，这已经把选项限制到了那一种实体上。不过，当你有一个共享的选项消息应用到多种实体类型、又想控制该消息中个别字段的使用时，选项目标就很有用。例如：

```proto
message MyOptions {
  optional string file_only_option = 1 [targets = TARGET_TYPE_FILE];
  optional int32 message_and_enum_option = 2 [targets = TARGET_TYPE_MESSAGE,
                                              targets = TARGET_TYPE_ENUM];
}

extend google.protobuf.FileOptions {
  optional MyOptions file_options = 50000;
}

extend google.protobuf.MessageOptions {
  optional MyOptions message_options = 50000;
}

extend google.protobuf.EnumOptions {
  optional MyOptions enum_options = 50000;
}

// 正确：该字段可用于文件选项
option (file_options).file_only_option = "abc";

message MyMessage {
  // 正确：该字段可同时用于消息和枚举选项
  option (message_options).message_and_enum_option = 42;
}

enum MyEnum {
  MY_ENUM_UNSPECIFIED = 0;
  // 错误：file_only_option 不能设置在枚举上。
  option (enum_options).file_only_option = "xyz";
}
```

## 生成你的类 {#generating}

要生成处理 `.proto` 文件中定义的消息类型所需的 Java、Kotlin、Python、C++、Go、Ruby、Objective-C 或 C# 代码，你需要对 `.proto` 文件运行 Protobuf 编译器 `protoc`。如果你尚未安装编译器，
请[下载软件包](/downloads)并按照
README 中的说明操作。对于 Go，你还需要为编译器安装一个特殊的代码生成器插件；你可以在 GitHub 上的 [golang/protobuf](https://github.com/golang/protobuf/)
仓库中找到它及安装说明。

协议编译器的调用方式如下：

```sh
protoc --proto_path=IMPORT_PATH --cpp_out=DST_DIR --java_out=DST_DIR --python_out=DST_DIR --go_out=DST_DIR --ruby_out=DST_DIR --objc_out=DST_DIR --csharp_out=DST_DIR path/to/file.proto
```

*   `IMPORT_PATH` 指定在解析 `import` 指令时查找 `.proto` 文件的目录。如果省略，则使用当前目录。
    可以通过多次传递 `--proto_path` 选项来指定多个导入目录；它们会按顺序被搜索。`-I=_IMPORT_PATH_`
    可以用作 `--proto_path` 的简写形式。

**注意：**相对于各自 `proto_path` 的文件路径在给定的二进制程序中必须全局唯一。例如，如果你有 `proto/lib1/data.proto` 和
`proto/lib2/data.proto`，这两个文件不能与
`-I=proto/lib1 -I=proto/lib2` 一起使用，因为 `import
"data.proto"` 究竟指哪个文件会有歧义。应当改用 `-Iproto/`，这样全局名称将是 `lib1/data.proto` 和 `lib2/data.proto`。

如果你在发布一个库、而其他用户可能直接使用你的消息，你应当在预期使用路径中包含一个唯一的库名，以避免文件名冲突。如果一个项目中有多个目录，最佳实践是倾向于把一个 `-I` 设置为项目的顶层目录。

*   你可以提供一个或多个*输出指令*：

    *   `--cpp_out` 在 `DST_DIR` 中生成 C++ 代码。更多信息请参阅
        [C++ 生成代码参考](/reference/cpp/cpp-generated)。
    *   `--java_out` 在 `DST_DIR` 中生成 Java 代码。更多信息请参阅
        [Java 生成代码参考](/reference/java/java-generated)。
    *   `--kotlin_out` 在 `DST_DIR` 中生成额外的 Kotlin 代码。更多信息请参阅
        [Kotlin 生成代码参考](/reference/kotlin/kotlin-generated)。
    *   `--python_out` 在 `DST_DIR` 中生成 Python 代码。更多信息请参阅
        [Python 生成代码参考](/reference/python/python-generated)。
    *   `--go_out` 在 `DST_DIR` 中生成 Go 代码。更多信息请参阅
        [Go 生成代码参考](/reference/go/go-generated-opaque)。
    *   `--ruby_out` 在 `DST_DIR` 中生成 Ruby 代码。更多信息请参阅
        [Ruby 生成代码参考](/reference/ruby/ruby-generated)。
    *   `--objc_out` 在 `DST_DIR` 中生成 Objective-C 代码。更多信息请参阅
        [Objective-C 生成代码参考](/reference/objective-c/objective-c-generated)。
    *   `--csharp_out` 在 `DST_DIR` 中生成 C# 代码。更多信息请参阅
        [C# 生成代码参考](/reference/csharp/csharp-generated)。
    *   `--php_out` 在 `DST_DIR` 中生成 PHP 代码。更多信息请参阅
        [PHP 生成代码参考](/reference/php/php-generated)。

    作为一项额外的便利功能，如果 `DST_DIR` 以 `.zip` 或 `.jar` 结尾，编译器会把输出写入一个具有给定名称的 ZIP 格式归档文件。`.jar` 输出还会按照 Java JAR 规范的要求附带一个清单（manifest）文件。注意，如果输出归档已存在，它将被覆盖。

*   你必须提供一个或多个 `.proto` 文件作为输入。可以一次指定多个 `.proto`
    文件。虽然这些文件以相对于当前目录的名称来命名，但每个文件必须位于某个 `IMPORT_PATH` 之内，以便编译器能够确定其规范名称。

## 文件位置 {#location}

尽量不要把 `.proto` 文件与其他语言的源代码放在同一目录中。可以考虑在项目根包之下创建一个用于存放 `.proto` 文件的
`proto` 子包。

### 位置应当与语言无关 {#location-language-agnostic}

在处理 Java 代码时，把相关的 `.proto` 文件放在 Java 源代码同一目录会很方便。然而，一旦有任何非 Java 代码使用同一批 proto，路径前缀就不再有意义。因此一般来说，应把 proto 放在相关的语言无关目录中，例如
`//myteam/mypackage`。

这条规则的例外情况是：可以明确这些 proto 只会在 Java 环境中使用，例如用于测试。

## 支持的平台 {#platforms}

有关以下方面的信息：

*   受支持的操作系统、编译器、构建系统和 C++ 版本，请参阅
    [基础 C++ 支持政策](https://opensource.google/documentation/policies/cplusplus-support)。
*   受支持的 PHP 版本，请参阅
    [受支持的 PHP 版本](https://cloud.google.com/php/getting-started/supported-php-versions)。

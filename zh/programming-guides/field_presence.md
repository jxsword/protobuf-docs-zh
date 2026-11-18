+++
title = "应用说明：字段存在性"
weight = 85
linkTitle = "字段存在性"
description = "解释 Protobuf 字段的各类存在性追踪规则。同时解释对带基本类型的单数 proto3 字段进行显式存在性追踪时的行为。"
type = "docs"
source_url = "https://protobuf.dev/programming-guides/field_presence/"
upstream_commit = "f72a6a648b34e9e098cbce1519bc9c8139105d66"
translated_at = "2026-11-19"
status = "translated"
translator = "agent"
+++

## 背景 {#background}

*字段存在性（field presence）*指的是 Protobuf 字段（field）是否具有值（value）这一概念。Protobuf 中存在性有两种不同的表现形式：*隐式存在性（implicit presence）*，即生成的消息（message）API 只存储字段值；以及*显式存在性（explicit presence）*，即 API 还会存储字段是否已被设置。

{{% alert title="Note" color="note" %}} 我们建议默认为 proto3 基本类型添加 `optional` 标记。这为迁移到版次（editions）提供了更平滑的路径，因为版次默认使用显式存在性。原因说明以及不适用此建议的情形，请参阅 [隐式存在性](/design-decisions/implicit-presence)。{{% /alert %}}

### 存在性规则 {#disciplines}

*存在性规则（presence discipline）*定义了在 *API 表示*与*序列化表示*之间进行转换的语义。*隐式存在性*规则依赖字段值本身在序列化（serialization）或反序列化（deserialization）时做出决策，而*显式存在性*规则则依赖显式的追踪（tracking）状态。

### *标签-值流*（线路格式）序列化中的存在性 {#presence-tag-value}

线路格式（wire format）是由带有标签（tag）的、*自定界（self-delimiting）*的值组成的流。根据定义，线路格式表示的是一系列*存在*的值。换言之，序列化结果中出现的每个值都代表一个*存在*的字段；此外，序列化结果不包含任何关于“不存在”值的信息。

proto 消息的生成 API 包含（反）序列化定义，用于在 API 类型与一串在定义上*存在*的（标签，值）对之间进行转换。这种转换被设计为在消息定义发生变更时保持向前兼容与向后兼容；然而，这种兼容性在反序列化线路格式的消息时会引入一些（可能令人意外的）注意事项：

-   序列化时，采用*隐式存在性*的字段若包含其默认值（default value），则不会被序列化。
    -   对于数值类型，默认值为 0。
    -   对于枚举（enum），默认值为取值为 0 的枚举项（enumerator）。
    -   对于字符串、bytes 和 repeated 字段，默认值为零长度值。
-   “空”的长度限定（length-delimited）值（例如空字符串）可以在序列化值中得到合法表示：就该值出现在线路格式中而言，该字段是“存在”的。然而，如果生成的 API 不追踪存在性，那么这些值可能不会被重新序列化；也就是说，空字段在经过一次序列化往返（round-trip）之后可能变为“不存在”。
-   反序列化时，重复的字段值可能会根据字段定义以不同方式处理。
    -   重复的 `repeated` 字段通常会追加到该字段的 API 表示中。（注意，序列化采用*紧凑编码（packed）*的 repeated 字段时，标签流中只会产生一个长度限定值。）
    -   重复的 `optional` 字段值遵循“最后一个值胜出”规则。
-   `oneof` 字段在 API 层面暴露了同一时间只能设置一个字段的不变式。然而，线路格式中可能包含多个名义上属于该 `oneof` 的（标签，值）对。与 `optional` 字段类似，生成的 API 遵循“最后一个值胜出”规则。
-   在生成的 proto2 API 中，枚举字段不会返回超出范围的值。然而，即使线路格式中的标签可被识别，超出范围的值也可能作为*未知字段（unknown fields）*存储在 API 中。

### *命名字段映射*格式中的存在性 {#presence-named-field}

Protobuf 消息可以表示为人类可读的文本形式。两种值得注意的格式是 TextFormat（由生成消息的 `DebugString` 方法输出的格式）和 JSON。

这些格式有各自的正确性要求，通常比*标签-值流*格式更严格。不过，TextFormat 在更大程度上模仿线路格式的语义，并且在某些情况下确实提供类似的语义（例如，将重复的名称-值映射追加到 repeated 字段）。特别地，与线路格式类似，TextFormat 只包含存在的字段。

然而，JSON 是一种严格得多的格式，无法合法地表示线路格式或 TextFormat 的某些语义。

-   值得注意的是，JSON *元素*在语义上是无序的，且每个成员必须具有唯一的名称。这与 TextFormat 针对 repeated 字段的规则不同。
-   与其他格式采用的*隐式存在性*规则不同，JSON 可能包含“不存在”的字段：
    -   JSON 定义了 `null` 值，可用于表示*已定义但不存在的字段*。
    -   repeated 字段的值可能会包含在格式化输出中，即使它们等于默认值（空列表）。
-   由于 JSON 元素是无序的，因此无法无歧义地解释“最后一个值胜出”规则。
    -   在大多数情况下，这没有问题：JSON 元素必须具有唯一的名称；repeated 字段值不是合法的 JSON，因此无需像 TextFormat 中那样对重复值加以处理。
    -   然而，这也意味着可能无法无歧义地解释 `oneof` 字段：如果存在多个分支（case），它们是无序的。

理论上，JSON *能够*以保持语义的方式表示存在性。然而在实践中，存在性的正确性可能因实现选择而异，尤其是在选择 JSON 作为与不使用 Protobuf 的客户端进行互操作的手段时。

### proto2 API 中的存在性 {#presence-proto2}

下表概述了 proto2 API 中的字段是否追踪存在性（既包括生成的 API，也包括动态反射（dynamic reflection））：

字段类型                                      | 显式存在性
-------------------------------------------- | -----------------
单数数值（整数或浮点数）                      | ✔️
单数枚举                                      | ✔️
单数字符串或 bytes                            | ✔️
单数消息                                      | ✔️
repeated                                      |
oneof                                         | ✔️
映射（map）                                   |

各类型的单数字段在生成的 API 中都显式追踪存在性。生成的消息接口包含用于查询字段存在性的方法。例如，字段 `foo` 有对应的 `has_foo` 方法。（具体名称遵循与字段访问器（accessor）相同的各语言命名约定。）这些方法在 Protobuf 实现内部有时被称为“hazzer”。

与单数字段类似，`oneof` 字段会显式追踪其成员中哪一个（如果有的话）包含值。例如，考虑下面这个 `oneof` 示例：

```protobuf
oneof foo {
  int32 a = 1;
  float b = 2;
}
```

视目标语言而定，生成的 API 通常会包含以下几个方法：

-   oneof 的 hazzer：`has_foo`
-   *oneof 分支*方法：`foo`
-   各成员的 hazzer：`has_a`、`has_b`
-   各成员的取值方法（getter）：`a`、`b`

repeated 字段和映射不追踪存在性：*空*的 repeated 字段与*不存在*的 repeated 字段之间没有区别。

### proto3 API 中的存在性 {#presence-proto3}

下表概述了 proto3 API 中的字段是否追踪存在性（既包括生成的 API，也包括动态反射）：

字段类型                                      | `optional` | 显式存在性
-------------------------------------------- | ---------- | -----------------
单数数值（整数或浮点数）                      | 否         |
单数数值（整数或浮点数）                      | 是         | ✔️
单数枚举                                      | 否         |
单数枚举                                      | 是         | ✔️
单数字符串或 bytes                            | 否         |
单数字符串或 bytes                            | 是         | ✔️
单数消息                                      | 否         | ✔️
单数消息                                      | 是         | ✔️
repeated                                      | 不适用     |
oneof                                         | 不适用     | ✔️
映射                                          | 不适用     |

与 proto2 API 类似，proto3 对 repeated 字段不显式追踪存在性。在没有 `optional` 标记时，proto3 API 对基本类型（数值、字符串、bytes 和枚举）也不追踪存在性。oneof 字段明确地暴露存在性，尽管可能不会像 proto2 API 那样生成同一组 hazzer 方法。

这种在没有 `optional` 标记时不追踪存在性的默认行为与 proto2 的行为不同。除非有特定理由，否则我们建议在 proto3 中使用 `optional` 标记。Protobuf 团队为何对隐式存在性感到遗憾、以及哪些情况下选择它仍然是合理的，请参阅 [隐式存在性](/design-decisions/implicit-presence)。

在*隐式存在性*规则下，就序列化而言，默认值与“不存在”是同义的。API 用户若想名义上“清除”一个字段（使其不会被序列化），只需将其设置为默认值即可。

在*隐式存在性*下，枚举类型字段的默认值是对应的取值为 0 的枚举项。按照 proto3 语法规则，所有枚举类型都必须拥有一个映射到 0 的枚举项。按照惯例，这是一个名为 `UNKNOWN` 或类似名称的枚举项。如果 0 值在名义上处于该应用合法值域之外，那么这种行为可以视为等同于*显式存在性*。

### 版次 API 中的存在性 {#presence-editions}

下表概述了版次 API 中的字段是否追踪存在性（既包括生成的 API，也包括动态反射）：

字段类型                                      | 显式存在性
-------------------------------------------- | -----------------
单数数值（整数或浮点数）                      | ✔️
单数枚举                                      | ✔️
单数字符串或 bytes                            | ✔️
单数消息&#8224;                               | ✔️
repeated                                      |
oneof&#8224;                                  | ✔️
映射                                          |

&#8224; 消息和 oneof 从未有过隐式存在性，并且版次不允许你设置 `field_presence = IMPLICIT`。

基于版次的 API 会像 proto2 一样显式追踪字段存在性，除非 `features.field_presence` 被设置为 `IMPLICIT`。与 proto2 API 类似，基于版次的 API 对 repeated 字段也不显式追踪存在性。

## 语义差异 {#semantic-differences}

当设置了默认值时，*隐式存在性*序列化规则与*显式存在性*追踪规则之间会产生可见的差异。对于数值、枚举或字符串类型的单数字段：

-   *隐式存在性*规则：
    -   默认值不会被序列化。
    -   合并（merge）时默认值*不会*被并入。
    -   要“清除”一个字段，就将它设置为其默认值。
    -   默认值可能意味着：
        -   该字段被显式设置为其默认值，而该值在应用特定的值域内是合法的；
        -   该字段通过设置默认值而被名义上“清除”；或者
        -   该字段从未被设置过。
    -   不生成 `has_` 方法（但请参阅此列表之后的说明）
-   *显式存在性*规则：
    -   显式设置的值总是会被序列化，包括默认值。
    -   未设置的字段在合并时永远不会被并入。
    -   显式设置的字段——包括默认值——在合并时*会*被并入。
    -   生成的 `has_foo` 方法指示字段 `foo` 是否已被设置（且未被清除）。
    -   必须使用生成的 `clear_foo` 方法来清除（即取消设置）该值。

{{% alert title="Note" color="note" %}}
在大多数情况下，不会为采用隐式存在性的成员生成 `has_` 方法。此行为的例外是 Dart：对于 proto3 的 proto 模式（schema）文件，它会生成 `has_` 方法。{{% /alert %}}

### 合并的注意事项 {#merging}

在*隐式存在性*规则下，合并值时会跳过任何取默认值的字段；没有任何信号可以区分该字段是从未被设置，还是被设置成了零。

这种合并行为会对依赖部分“补丁”（patch）式更新的协议产生影响。由于不追踪字段存在性，你可以用非默认值（例如 `42`）来发出“该字段应被替换”的信号，但无法用默认值（例如 `0`）来发出同样的信号。

在这种情况下，要把字段更新为默认值就需要某种外部机制，例如 `FieldMask`。然而，如果*确实*追踪了存在性，那么所有显式设置的值——即使是默认值——都会被合并到目标中。

### 变更兼容性的注意事项 {#change-compatibility}

将字段在*显式存在性*与*隐式存在性*之间来回更改，对于线路格式的序列化值而言是二进制兼容的变更。然而，消息的序列化表示可能有所不同，具体取决于序列化时使用的是消息定义的哪个版本（version）。具体来说，当“发送方”将某个字段显式设置为其默认值时：

-   遵循*隐式存在性*规则的序列化值不包含该默认值，即使它是被显式设置的。
-   遵循*显式存在性*规则的序列化值包含每一个“存在”的字段，即使其中包含默认值。

这种变更是否安全取决于应用的语义。例如，考虑两个拥有不同版本消息定义的客户端。

客户端 A 使用下面的消息定义，其中的字段 `foo` 遵循*显式存在性*序列化规则：

```protobuf
syntax = "proto3";
message Msg {
  optional int32 foo = 1;
}
```

客户端 B 使用同一消息的另一个定义，区别在于它遵循*无存在性（no presence）*规则：

```protobuf
syntax = "proto3";
message Msg {
  int32 foo = 1;
}
```

现在，考虑这样一个场景：两个客户端通过反复反序列化和重新序列化来交换“同一”消息，客户端 A 在此过程中观察 `foo` 的存在性：

```protobuf
// 客户端 A：
Msg m_a;
m_a.set_foo(1);                  // 非默认值
assert(m_a.has_foo());           // 正常
Send(m_a.SerializeAsString());   // 发送给客户端 B

// 客户端 B：
Msg m_b;
m_b.ParseFromString(Receive());  // 来自客户端 A
assert(m_b.foo() == 1);          // 正常
Send(m_b.SerializeAsString());   // 发送给客户端 A

// 客户端 A：
m_a.ParseFromString(Receive());  // 来自客户端 B
assert(m_a.foo() == 1);          // 正常
assert(m_a.has_foo());           // 正常
m_a.set_foo(0);                  // 默认值
Send(m_a.SerializeAsString());   // 发送给客户端 B

// 客户端 B：
Msg m_b;
m_b.ParseFromString(Receive());  // 来自客户端 A
assert(m_b.foo() == 0);          // 正常
Send(m_b.SerializeAsString());   // 发送给客户端 A

// 客户端 A：
m_a.ParseFromString(Receive());  // 来自客户端 B
assert(m_a.foo() == 0);          // 正常
assert(m_a.has_foo());           // 失败
```

如果客户端 A 依赖 `foo` 的*显式存在性*，那么经过客户端 B 的“往返”从客户端 A 的角度看就是有损的。在这个例子中，这不是一个安全的变更：客户端 A（通过 `assert`）要求该字段存在；即使不通过 API 做任何修改，在这种依赖具体值与对端的情形下，该要求也会落空。

## 如何在 proto3 中启用*显式存在性* {#enable-explicit-proto3}

以下是在 proto3 中使用字段追踪支持的常规步骤：

1.  在 `.proto` 文件中添加一个 `optional` 字段。
1.  运行 `protoc`（至少为 v3.15，或使用 `--experimental_allow_proto3_optional` 标志的 v3.12）。
1.  在应用代码中使用生成的 “hazzer” 方法和 “clear” 方法，而不是比较或设置默认值。

### `.proto` 文件变更 {#proto-file-changes}

下面是一个 proto3 消息示例，其中的字段同时遵循*无存在性*与*显式存在性*语义：

```protobuf
syntax = "proto3";
package example;

message MyMessage {
  // 隐式存在性：
  int32 not_tracked = 1;

  // 显式存在性：
  optional int32 tracked = 2;
}
```

### `protoc` 调用 {#protoc-invocation}

自 [v3.15.0](https://github.com/protocolbuffers/protobuf/releases/tag/v3.15.0) 发布起，proto3 消息的存在性追踪默认启用；在此之前（直至 [v3.12.0](https://github.com/protocolbuffers/protobuf/releases/tag/v3.12.0)），在 protoc 中使用存在性追踪时需要 `--experimental_allow_proto3_optional` 标志。

### 使用生成的代码

带*显式存在性*（`optional` 标记）的 proto3 字段所生成的代码（generated code），与 proto2 文件中的生成代码相同。

下面“隐式存在性”示例所用的定义：

```protobuf
syntax = "proto3";
package example;
message Msg {
  int32 foo = 1;
}
```

下面“显式存在性”示例所用的定义：

```protobuf
syntax = "proto3";
package example;
message Msg {
  optional int32 foo = 1;
}
```

在这些示例中，函数 `GetProto` 会构造并返回一个内容未指定的 `Msg` 类型消息。

#### C++ 示例 {#cpp-example}

隐式存在性：

```cpp
Msg m = GetProto();
if (m.foo() != 0) {
  // “清除”该字段：
  m.set_foo(0);
} else {
  // 默认值：字段此前可能并不存在。
  m.set_foo(1);
}
```

显式存在性：

```c++
Msg m = GetProto();
if (m.has_foo()) {
  // 清除该字段：
  m.clear_foo();
} else {
  // 字段不存在，因此设置它。
  m.set_foo(1);
}
```

#### C# 示例 {#csharp-example}

隐式存在性：

```c#
var m = GetProto();
if (m.Foo != 0) {
  // “清除”该字段：
  m.Foo = 0;
} else {
  // 默认值：字段此前可能并不存在。
  m.Foo = 1;
}
```

显式存在性：

```c#
var m = GetProto();
if (m.HasFoo) {
  // 清除该字段：
  m.ClearFoo();
} else {
  // 字段不存在，因此设置它。
  m.Foo = 1;
}
```

#### Go 示例 {#go-example}

隐式存在性：

```go
m := GetProto()
if m.Foo != 0 {
  // “清除”该字段：
  m.Foo = 0
} else {
  // 默认值：字段此前可能并不存在。
  m.Foo = 1
}
```

显式存在性：

```go
m := GetProto()
if m.Foo != nil {
  // 清除该字段：
  m.Foo = nil
} else {
  // 字段不存在，因此设置它。
  m.Foo = proto.Int32(1)
}
```

#### Java 示例 {#java-example}

这些示例使用 `Builder`（构建器）来演示清除操作。仅检查存在性以及从 `Builder` 获取值时，所用的 API 与消息类型相同。

隐式存在性：

```java
Msg.Builder m = GetProto().toBuilder();
if (m.getFoo() != 0) {
  // “清除”该字段：
  m.setFoo(0);
} else {
  // 默认值：字段此前可能并不存在。
  m.setFoo(1);
}
```

显式存在性：

```java
Msg.Builder m = GetProto().toBuilder();
if (m.hasFoo()) {
  // 清除该字段：
  m.clearFoo()
} else {
  // 字段不存在，因此设置它。
  m.setFoo(1);
}
```

#### Python 示例 {#python-example}

隐式存在性：

```python
m = example.Msg()
if m.foo != 0:
  # “清除”该字段：
  m.foo = 0
else:
  # 默认值：字段此前可能并不存在。
  m.foo = 1
```

显式存在性：

```python
m = example.Msg()
if m.HasField('foo'):
  # 清除该字段：
  m.ClearField('foo')
else:
  # 字段不存在，因此设置它。
  m.foo = 1
```

#### Ruby 示例 {#ruby-example}

隐式存在性：

```ruby
m = Msg.new
if m.foo != 0
  # “清除”该字段：
  m.foo = 0
else
  # 默认值：字段此前可能并不存在。
  m.foo = 1
end
```

显式存在性：

```ruby
m = Msg.new
if m.has_foo?
  # 清除该字段：
  m.clear_foo
else
  # 字段不存在，因此设置它。
  m.foo = 1
end
```

#### Javascript 示例 {#js-example}

隐式存在性：

```js
var m = new Msg();
if (m.getFoo() != 0) {
  // “清除”该字段：
  m.setFoo(0);
} else {
  // 默认值：字段此前可能并不存在。
  m.setFoo(1);
}
```

显式存在性：

```js
var m = new Msg();
if (m.hasFoo()) {
  // 清除该字段：
  m.clearFoo()
} else {
  // 字段不存在，因此设置它。
  m.setFoo(1);
}
```

#### Objective-C 示例 {#objc-example}

隐式存在性：

```objective-c
Msg *m = [Msg message];
if (m.foo != 0) {
  // “清除”该字段：
  m.foo = 0;
} else {
  // 默认值：字段此前可能并不存在。
  m.foo = 1;
}
```

显式存在性：

```objective-c
Msg *m = [Msg message];
if ([m hasFoo]) {
  // 清除该字段：
  [m clearFoo];
} else {
  // 字段不存在，因此设置它。
  m.foo = 1;
}
```

## 速查表 {#cheat}

**Proto2：**

是否追踪字段存在性？

字段类型               | 是否追踪？
---------------------- | --------
单数字段               | 是
单数消息字段           | 是
oneof 中的字段         | 是
repeated 字段与映射    | 否

**Proto3：**

是否追踪字段存在性？

字段类型               | 是否追踪？
---------------------- | ------------------------
*其他*单数字段         | 定义为 `optional` 时
单数消息字段           | 是
oneof 中的字段         | 是
repeated 字段与映射    | 否

**版次 2023：**

是否追踪字段存在性？

字段类型（按优先级从高到低）                                        | 是否追踪？
-------------------------------------------------------------------- | --------
repeated 字段与映射                                                 | 否
消息与 oneof 字段                                                   | 是
当 `features.field_presence` 设置为 `IMPLICIT` 时的其他单数字段     | 否
所有其他字段                                                        | 是

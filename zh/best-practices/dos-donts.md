+++
title = "Proto 最佳实践"
weight = 90
description = "分享经过验证的 Protobuf 模式编写最佳实践。"
type = "docs"
aliases = "/programming-guides/dos-donts"
source_url = "https://protobuf.dev/best-practices/dos-donts/"
upstream_commit = "f72a6a648b34e9e098cbce1519bc9c8139105d66"
translated_at = "2026-11-18"
status = "translated"
translator = "agent"
+++

客户端和服务端永远不会在完全相同的时刻被更新——即使你尝试同时更新它们也是如此，其中一方仍可能被回滚。不要以为客户端和服务端已保持同步，就可以放心地做出破坏性变更（breaking change）。

<a id="dont-re-use-a-tag-number"></a>

## **不要**重用标签编号 {#reuse-number}

绝不要重用标签（tag）编号。它会破坏反序列化（deserialization）。即使你认为没有任何人正在使用该字段，也不要重用标签编号。只要这个变更曾经上线过，某处的日志里就可能存有你 proto 的序列化（serialization）版本。或者，另一台服务器上可能还留有会因此出问题的旧代码。

<a id="do-reserve-tag-numbers-for-deleted-fields"></a>

## **要**为已删除的字段保留标签编号 {#reserve-tag-numbers}

删除不再使用的字段（field）时，请保留其标签编号，以免日后有人不小心重用它。只需 `reserved 2, 3;` 就够了，无需指定类型（这还能帮你精简依赖！）。你也可以保留名称，避免已被删除的字段名被回收再用：`reserved foo, bar;`。参见关于[保留字段编号](/programming-guides/editions#fieldreserved)和[保留字段名](/programming-guides/editions#reserved-field-names)的文档。

<a id="do-reserve-numbers-for-deleted-enum-values"></a>

## **要**为已删除的枚举值保留编号 {#reserve-deleted-numbers}

删除不再使用的枚举（enum）值时，请保留其编号，以免日后有人不小心重用它。只需 `reserved 2, 3;` 就够了。你也可以保留名称，避免已被删除的值名称被回收再用：`reserved
FOO, BAR;`。另参见[枚举保留值](/programming-guides/editions#reserved)

<a id="do-put-new-enum-aliases-last"></a>

## **要**把新的枚举别名放在最后 {#enum-aliases-last}

添加新的枚举别名（alias）时，请把新名称放在最后，给各服务（service）留出跟进的时间。

要安全地移除原始名称（如果它正被用于数据交换——而这本[不应](#text-format-interchange)发生），你必须执行以下步骤：

*   在旧名称下方添加新名称，并将旧名称弃用（序列化器将继续使用旧名称）

*   待新模式（schema）在所有解析器上完成上线后，交换这两个名称的顺序（序列化器将开始使用新名称，解析器则两者都接受）

*   待所有序列化器都拿到了该版本的模式后，即可删除被弃用的名称。

> **注意：** 虽然理论上客户端不应把旧名称用于数据交换，但遵循上述步骤仍是一种更为周到的做法，对于广泛使用的枚举名称尤其如此。

<a id="dont-change-the-type-of-a-field"></a>

## **不要**更改字段类型 {#change-type}

几乎任何情况下都不要更改字段的类型；它会破坏反序列化，后果与重用标签编号相同。[Protobuf 文档](/programming-guides/editions#updating)列出了旧二进制编码数据可以在不同类型下被成功解析（parse）的情形（例如在 `int32`、`uint32`、`int64` 和 `bool` 之间互换）。然而，即便新模式能够成功解析旧数据，要安全地上线字段类型变更也可能相当困难。

<a id="dont-add-a-required-field"></a>

## **不要**添加 required 字段 {#add-required}

绝不要添加 required 字段；请改为添加 `// required` 注释，用它记录 API 契约。required 字段被太多人视为有害，以至于 proto3 已将其彻底移除。请把所有字段都声明为 optional 或 repeated。你永远无法预知一个消息（message）类型会存在多久，也无法预知四年之后——当它在逻辑上已不再必需、而 proto 里却仍声明为 required 时——是否会有人被迫用空字符串或 0 来填充你的 required 字段。

proto3 中没有 `required` 字段，因此本条建议不适用。

<a id="dont-make-a-message-with-lots-of-fields"></a>

## **不要**创建包含大量字段的消息 {#lots-of-fields}

不要创建含有“大量”（比如说数百个）字段的消息。在 C++ 中，无论字段是否有值，每个字段都会给内存中对象的大小增加约 65 比特（其中 8 字节是指针；如果字段声明为 optional，位域（bitfield）中还要再占 1 比特，用于追踪该字段是否已被设置）。当你的 proto 膨胀得过大时，生成代码（generated code）甚至可能无法编译（例如，Java 对单个方法的大小有硬性限制）。

<a id="do-include-an-unspecified-value-in-an-enum"></a>

## **要**在枚举中包含未指定值 {#unspecified-enum}

枚举应在声明中把一个默认的 `FOO_UNSPECIFIED` 值列为第一个值。当枚举新增值时，旧客户端会把该字段视为未设置（unset），其 getter 将返回默认值（default value）；如果不存在默认值，则返回第一个声明的值。为了与 [proto 枚举][proto-enums] 保持一致的行为，第一个声明的枚举值应当是默认的 `FOO_UNSPECIFIED` 值，并应使用标签编号 0。把这个默认值声明成一个具有实际语义的值看似诱人，但作为一般规则请不要这样做——这样你的协议才能随着新枚举值的陆续添加而顺利演进。在同一容器消息下声明的所有枚举值都位于同一个 C++ 命名空间（namespace）中，因此请给未指定值加上枚举名作为前缀，以避免编译错误。如果你确定永远不需要跨语言（cross-language）常量，使用 `int32` 也能保留未知值，并且生成的代码更少。请注意，[proto 枚举][proto-enums]要求第一个值为 0，并且能够对未知枚举值进行往返（round-trip）处理（即先反序列化再序列化）。

[example-unspecified]: http://cs/#search/&q=file:proto%20%22_UNSPECIFIED%20=%200%22&type=cs
[proto-enums]: /programming-guides/editions#enum

<a id="dont-use-cc-macro-constants-for-enum-values"></a>

## **不要**将 C/C++ 宏常量用作枚举值 {#macro-constants}

使用 C++ 语言已有定义的词——特别是诸如 `math.h` 这类头文件中定义的词——如果这些头文件中任何一个的 `#include` 语句出现在 `.proto.h` 的 `#include` 语句之前，就可能引发编译错误。请避免使用 `NULL`、`NAN`、`DOMAIN` 这类宏常量作为枚举值。

<a id="dont-use-any"></a>

## **要**尽量用扩展而非 `Any` {#avoid-any}

如果你打算使用 `Any`，请先再次确认扩展（extension）能否满足该用例；如果可以，请优先使用扩展。

`Any` 在 Proto3 中被创造出来，目的是取代扩展。然而它存在不少设计缺陷（参见[我们更倾向于用扩展取代 Any](/design-decisions/extensions-over-any)）。对于大多数用例，请优先使用扩展。

`Any` 真正满足的主要用例是一种不常见的场景：横向基础设施需要传递完全任意的消息，而为每一种可能的合法类型都声明一个扩展并不现实。

未来，Protobuf 可能会引入一个新概念，在不带这些设计缺陷的前提下满足 `Any` 的各类用例，但目前尚无具体计划。

<a id="do-use-well-known-types-and-common-types"></a>

## **要**使用知名类型和常用类型 {#well-known-common}

强烈建议使用下面这些常用的共享类型。例如，既然已有非常合适的常用类型，就不要在代码中使用 `int32 timestamp_seconds_since_epoch` 或 `int64 timeout_millis`！

<a id="well-known-types"></a><a id="common-types"></a>

*   [`duration`](https://github.com/protocolbuffers/protobuf/blob/main/src/google/protobuf/duration.proto) 是一个带符号、固定长度的时间跨度（例如 42s）。
*   [`timestamp`](https://github.com/protocolbuffers/protobuf/blob/main/src/google/protobuf/timestamp.proto) 是一个不依赖任何时区或日历的时间点（例如 2017-01-15T01:30:15.01Z）。
*   [`interval`](https://github.com/googleapis/googleapis/blob/master/google/type/interval.proto) 是一个不依赖时区或日历的时间区间（例如 2017-01-15T01:30:15.01Z - 2017-01-16T02:30:15.01Z）。
*   [`date`](https://github.com/googleapis/googleapis/blob/master/google/type/date.proto) 是一个完整的日历日期（例如 2005-09-19）。
*   [`month`](https://github.com/googleapis/googleapis/blob/master/google/type/month.proto) 是一年中的某个月份（例如 April）。
*   [`dayofweek`](https://github.com/googleapis/googleapis/blob/master/google/type/dayofweek.proto) 是一周中的某一天（例如 Monday）。
*   [`timeofday`](https://github.com/googleapis/googleapis/blob/master/google/type/timeofday.proto) 是一天中的某个时刻（例如 10:42:23）。
*   [`field_mask`](https://github.com/protocolbuffers/protobuf/blob/main/src/google/protobuf/field_mask.proto) 是一组符号化的字段路径（例如 f.b.d）。
*   [`postal_address`](https://github.com/googleapis/googleapis/blob/master/google/type/postal_address.proto) 是一个邮政地址（例如 1600 Amphitheatre Parkway Mountain View, CA 94043 USA）。
*   [`money`](https://github.com/googleapis/googleapis/blob/master/google/type/money.proto) 是带币种类型的金额（例如 42 USD）。
*   [`latlng`](https://github.com/googleapis/googleapis/blob/master/google/type/latlng.proto) 是一对纬度/经度（例如纬度 37.386051、经度 -122.083855）。
*   [`color`](https://github.com/googleapis/googleapis/blob/master/google/type/color.proto) 是 RGBA 色彩空间中的一种颜色。

**注意：** “知名类型（Well-Known Types）”（如 `Duration` 和 `Timestamp`）随 Protobuf 编译器一同提供，而“常用类型（Common Types）”（如 `Date` 和 `Money`）则不然。要使用常用类型，你可能需要添加对 [googleapis 仓库](https://github.com/googleapis/googleapis)的依赖。

<a id="do-define-widely-used-message-types-in-separate-files"></a>

## **要**将消息类型定义在单独的文件中 {#separate-files}

定义 proto 模式时，每个文件应当只有一个顶层入口点（导出的消息、导出的枚举、服务或扩展）。这会让重构更容易：文件彼此分离之后，直接移动文件要比从包含其他消息的文件中抽取消息容易得多。遵循这一实践还有助于让 proto 模式文件保持较小的体量，从而提升可维护性并减少传递依赖的膨胀。

符号可见性（`export` / `local`）为内部辅助类型放宽了这种严格分离：一个 `.proto` 文件可以包含多个 `local message` 或 `local enum` 定义，用以支撑单一的顶层入口点（例如为某个 `service` 提供支撑的远程过程调用（RPC）请求/响应消息），前提是这些辅助类型保持为 local，并且不会被导入到其他文件中。

在复用方面，消息和枚举应当是**原子性**的。嵌套类型（nested type）——即定义在另一个消息内部的消息或枚举——天然只对其父容器私有。在 `STRICT` 符号可见性下，嵌套实体完全无法被其他 `.proto` 文件导出或导入。你不应把另一个消息的嵌套类型当作可复用的词汇来使用。任何打算在其父文件之外被独立复用的符号，都应当在自己的 `.proto` 文件中定义为顶层的 `export message` 或 `export enum`。

如果某个类型会在你的项目之外被广泛使用，请考虑把它单独放进一个没有任何依赖的文件中。这样任何人都能轻松使用这些类型，而不会引入你其他 proto 文件中的传递依赖。

关于这一主题的更多信息，请参见 [1-1-1 规则](/best-practices/1-1-1)。

<a id="dont-change-the-default-value-of-a-field"></a>

## **不要**更改字段的默认值 {#change-default-value}

几乎任何情况下都不要更改 proto 字段的默认值。这会导致客户端与服务端之间的版本偏差：当双方的构建分处 proto 变更的前后两侧时，读取同一个未设置值的客户端与服务端会得到不同的结果。Proto3 已移除设置默认值的能力。

<a id="dont-go-from-repeated-to-scalar"></a>

## **不要**把 repeated 改为标量 {#repeated-to-scalar}

虽然不会导致崩溃，但你会丢失数据。对 JSON 而言，是否为 repeated 的不匹配会导致整条*消息*丢失。对数值型 proto3 字段和 proto2 的 `packed` 字段而言，从 repeated 改为标量（scalar）会丢失该*字段*中的全部数据。对非数值型 proto3 字段和未加注解的 proto2 字段而言，从 repeated 改为标量的结果是“最后反序列化的值胜出”。

从标量改为 repeated 在 proto2 中、以及在使用 `[packed=false]` 的 proto3 中是可行的，因为对二进制序列化（serialization）而言，标量值会变成单元素列表。

<a id="do-follow-the-style-guide-for-generated-code"></a>

## **要**让生成代码遵循样式指南 {#follow-style-guide}

proto 生成代码会被普通代码引用。请确保 `.proto` 文件中的选项不会导致生成违反样式指南（style guide）的代码。例如：

*   `java_outer_classname` 应遵循 https://google.github.io/styleguide/javaguide.html#s5.2.2-class-names

*   `java_package` 和 `java_alt_package` 应遵循 https://google.github.io/styleguide/javaguide.html#s5.2.1-package-names

*   `package` 虽然在 `java_package` 缺席时也会用于 Java，但它始终直接对应 C++ 命名空间，因此应遵循 https://google.github.io/styleguide/cppguide.html#Namespace_Names。如果这些样式指南相互冲突，Java 请以 `java_package` 为准。

*   `ruby_package` 应采用 `Foo::Bar::Baz` 的形式，而不是 `Foo.Bar.Baz`。

<a id="never-use-text-format-messages-for-interchange"></a>

## **不要**将文本格式消息用于数据交换 {#text-format-interchange}

文本格式（text format）和 JSON 这类基于文本的序列化格式把字段和枚举值表示为字符串。因此，一旦某个字段或枚举值被重命名，或者新增了某个字段、枚举值或扩展，用旧代码反序列化这些格式的 Protobuf 消息就会失败。数据交换请尽可能使用二进制序列化，文本格式只用于人工编辑和调试。

如果你在 API 中使用转换为 JSON 的 proto，或者用它来存储数据，那么你可能根本无法安全地重命名字段或枚举。

<a id="never-rely-on-serialization-stability-across-builds"></a>

## **绝不**要依赖跨构建的序列化稳定性 {#serialization-stability}

proto 序列化的稳定性在不同二进制文件之间、乃至同一二进制文件的不同构建之间都没有保证。例如在构建缓存键时，不要依赖这一点。

<a id="dont-generate-java-protos-in-the-same-java-package-as-other-code"></a>

## **不要**把 Java proto 生成到与其他代码相同的 Java 包中 {#generate-java-protos}

请把 Java proto 源码生成到与手写 Java 源码相互独立的包中。`package`、`java_package` 和 `java_alt_api_package` 选项控制[生成的 Java 源码被输出到哪里](/reference/java/java-generated#package)。请确保手写的 Java 源代码不会同时位于该包中。一种常见做法是把 proto 生成到项目中的一个 `proto` 子包里，该子包**只**包含这些 proto（也就是说，不含任何手写源代码）。

## **要**从 .proto 包派生 Java 包（如果发生覆写） {#derive-java-package}

设置 `java_package` 可能会在生成代码中引入 .proto 语义下原本不存在的全限定名冲突。例如，下面这两个文件尽管其全限定名在原始模式中并不冲突，却可能在生成代码中产生冲突：

```proto
package x;
option java_package = "com.example.proto";
message Abc {}
```

```proto
package y;
option java_package = "com.example.proto";
message Abc {}
```

为避免这些问题，绝不要在两个设置了不同 .proto 包的文件中设置相同的 `java_package`。

最佳实践是建立一种本地命名模式：让包名从 .proto 包派生而来。例如，一个遵循最佳实践、使用 `package y` 的文件可以统一设置 `option java_package =
"com.example.proto.y"`。

本指南同样适用于任何其他可以覆写包名的语言专属选项。

## 避免将语言关键字用作字段名 {#avoid-keywords}

如果消息、字段、枚举或枚举值的名称恰好是读写该字段的语言中的关键字，Protobuf 可能会更改字段名，其访问方式也可能与普通字段不同。例如，参见[关于 Python 的这条警告](/reference/python/python-generated#keyword-conflicts)。

你还应避免在文件路径中使用关键字，因为这同样可能引发问题。

## **要**为远程过程调用（RPC）API 和存储使用不同的消息 {#separate-types-for-storage}

为 API 和长期存储复用相同的消息看似方便，可以减少样板代码以及消息之间相互转换的开销。

然而，长期存储与在线远程过程调用（RPC）服务的需求日后往往会逐渐分化。即便两类消息起初在很大程度上相互重复，也使用彼此独立的类型，这会让你在更改存储格式时不受外部客户端的影响。请对代码分层，让各模块要么处理客户端 proto，要么处理存储 proto，要么负责两者之间的转换。

维护这一转换层确实有成本，但一旦你拥有了客户端、并且不得不进行第一次存储变更时，这笔投入很快就会得到回报。

## **不要**为现在只有两种状态、将来可能有更多状态的事物使用布尔值 {#bad-bools}

如果你在某个字段上使用布尔值，请确保该字段描述的确实只有两种可能的状态（永远如此，而不只是现在和不久的将来）。使用枚举所带来的未来灵活性通常是值得的，即使它在首次引入时只有两个值。

```
message Photo {
  // 差：如果是 GIF 则为 true。
  optional bool gif;

  // 好：所引用照片的文件格式（例如 GIF、WebP、PNG）。
  optional PhotoType type;
}
```

## **要**设置 java_outer_classname（版次 2024 之前） {#java-outer-classname}

每个 proto 模式定义文件都应把选项 `java_outer_classname` 设置为对应的 `.proto` 文件名去掉 '.' 并转换为 TitleCase 后的名称。例如，`student_record_request.proto` 文件应设置：

```java
option java_outer_classname = "StudentRecordRequestProto";
```

版次 2024 文件的默认行为已与本建议保持一致，因此在使用版次 2024 或更高版次时，不应再设置该选项。

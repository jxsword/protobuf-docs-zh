

+++
title = "隐式存在性"
weight = 91
description = "阐述 Protobuf 团队为何对隐式存在性感到遗憾"
type = "docs"
source_url = "https://protobuf.dev/design-decisions/implicit-presence/"
upstream_commit = "f72a6a648b34e9e098cbce1519bc9c8139105d66"
translated_at = "2026-11-19"
status = "translated"
translator = "agent"
+++

隐式存在性（implicit presence）是 Protobuf 团队感到遗憾的一个设计决策——它是 proto3 的一项行为：单数标量字段（singular scalar field）没有 hazzer（用于设置 hasbit 的内联辅助方法），并且值 `0`、`false` 或 `""` 与“从未设置”无法区分。

我们不建议为新字段使用隐式存在性。

*   在 proto3 中，最好为字段加上 `optional` 标记。不过这只是弱指导性的建议；如果你仍在使用 Go Open API，那么你可能有充分的理由选择偏好隐式存在性字段。
*   今后，显式存在性（explicit presence）是 [Protobuf 版次（Editions）](/editions/overview)中无需声明即默认生效的选择。

有关存在性在各语法方言（dialect）中如何表现的操作细节，请参阅[字段存在性（field presence）](/programming-guides/field_presence)应用说明。本页讨论的是*为什么*。

## 什么是隐式存在性 {#what}

[字段存在性](/programming-guides/field_presence)指的是消息（message）是否追踪某个字段曾被设置，而不论它被设置成了什么值。

*   在**显式存在性**下，消息会把一个存在性位（presence bit）与值存储在一起，并生成 `has_foo()` hazzer。设置 `foo = 0` 会使字段变为存在并写入线路（wire）；清除该字段则使其变为不存在。
*   在**隐式存在性**下，消息只存储值本身，不生成任何 hazzer。设置 `foo = 0` 与清除 `foo` 或从未触碰该字段无法区分，且 `0` 永远不会被写入线路。

显式或隐式存在性之间的选择只适用于单数的数值类型、`bool`、`string`、`bytes` 和 `enum` 字段。消息字段和 `oneof` 成员始终是显式存在性，而 repeated 字段和映射始终是隐式存在性。

### proto3 {#proto3}

在 proto3 中，隐式存在性是这些字段类型的默认行为，而 `optional` 关键字则让你重新选回显式存在性：

```proto
syntax = "proto3";

message UserAccount {
  // 隐式存在性（proto3 默认行为）。
  // 不生成 has_login_count()，login_count = 0 与未设置无法区分，
  // 且 0 永远不会被序列化。
  int32 login_count = 1;

  // 显式存在性（推荐）。
  // 会生成 has_display_name()，并且 display_name = "" 会被序列化。
  optional string display_name = 2;
}
```

### 版次（Editions） {#editions}

版次移除了 `optional` 关键字，并用 [`field_presence` 特性（feature）](/editions/features#field_presence)取而代之，该特性默认为 `EXPLICIT`。如今，隐式存在性成了你必须专门设置才能启用的行为：

```proto
edition = "2023";

message UserAccount {
  // 显式存在性，无需任何关键字。
  string display_name = 1;

  // 隐式存在性需要显式选择启用。
  int32 login_count = 2 [features.field_presence = IMPLICIT];
}
```

> **注意：** 隐式存在性在 proto2 中并不存在。proto2 的每一个单数字段都采用显式存在性。

## 引入隐式存在性的原因 {#why-introduced}

引入隐式存在性并不是因为它自身的语义，而是为了支持[开放式结构体 API（open struct API）](/design-decisions/opaque-apis)。

在没有零成本值可选性（zero-cost value optionality）的语言中，公开的结构体字段无法携带存在性位；表示“未设置”的唯一办法是把字段装箱（box）成指针。proto3 的前提假设是：如果数据模型干脆抹去“未设置”与“设置为默认值”之间的区分，生成的代码就可以是由未装箱的公开字段构成的普通结构体——没有访问器（accessor），也没有 `hasbits`——而且这笔交易足够划算，值得为此在语义上做出妥协。

proto3 最初的设计文档是这样表述的：

> 移除基本类型值字段（primitive value field）的字段存在性逻辑，移除 required 字段，移除默认值。这使得 Proto3 在采用开放式结构体表示时（如在 Android Java、Objective-C 或 Go 这类语言中）实现起来容易得多。

这一设计理据建立在两个断言之上：其一，开放式结构体能让 protobuf 的实现明显更容易；其二，存在性追踪（presence tracking）对大多数字段而言纯属开销。事实证明，这两个断言都不成立。

## 开放式结构体的前提并未成立 {#open-structs}

Google 后来意识到，开放式结构体对各种实现的约束过强，正如[我们更青睐 Opaque API](/design-decisions/opaque-apis)一文所解释的那样。

因此，隐式存在性当初旨在解锁的那种 API 形态，如今已不再被视为好的设计，而它为此放弃的语义却依然存在。

## 它并不更快 {#performance}

关于隐式存在性最顽固的一个看法是：不去维护 hasbit 就意味着更少的工作。事实证明，这一点在实践中站不住脚。

显式存在性把存在性信息打包进消息开头的密集 32 位字中。这种密集性正是关键——它让针对整条消息的操作只需一次加载就能对许多字段做出判断：

*   **批量跳过。** 在 `Clear()`、`ByteSizeLong()` 和 `MergeFrom()` 中，C++ 代码生成器（code generator）用一次掩码测试（`BatchCheckHasBit(cached_has_bits, 0x000000ffU)`）来门控一组字段，还可以用一次横跨多个 has-word 的测试来门控宽消息的整片区域。不存在的字段会被直接跳过，其内存完全不会被触碰——这一点很重要，因为真实的消息是稀疏的，而冷字段恰恰是你最不想拉进缓存的那一类。
*   **无分支的大小计算。** 对于一组定宽字段，`ByteSizeLong()` 用 `popcount(mask & cached_has_bits) * size` 计算整组字段的贡献，没有任何分支，也不用加载任何一个字段值。代码生成器把这一优化限定在满足 `has_presence()` 的字段上，因为只有当该位是权威判定依据时它才成立。

隐式存在性则放弃了这一切。存在性与值绑定在一起，要判断某个字段是否参与运算，就必须加载该字段并与零作比较——每个字段如此、每次如此，遍及整个结构体。

而就在最近，我们实际上已开始让隐式存在性字段也拥有 hasbit：这些位只是提示，某一位置位意味着“可能存在”，因此访问器仍然必须比较字段值；但实践证明，它们所带来的批量跳过是一项有益的优化。

一旦实现了这一优化，隐式存在性字段每个字段的工作量实际上严格*多于*显式存在性：显式存在性字段测试一个位即可行动，而隐式存在性字段要先测试提示位，*然后*还要加载并比较字段值。

## 语义是“糟糕的” {#semantics}

隐式存在性并没有消除存在性这一概念。它把零和空字符串变成了魔法值，并把存在性与之绑定。凡是系统需要谈论什么*被设置过*（而不是值*是什么*）的地方，这种区分都会重新浮现。

### 合并 {#merging}

`MergeFrom` 会把源消息中存在的字段复制并覆盖到目标消息上。在隐式存在性下，被设置为零的字段并不存在，因此不会参与合并——这意味着一次合并可能产生一个在两个输入中都不曾存在的值。

最典型的例证是一个知名类型（well-known type）。`google.protobuf.Timestamp` 是随 proto3 一同推出的，因此它的两个字段都是隐式存在性：

```proto
syntax = "proto3";

package google.protobuf;

message Timestamp {
  int64 seconds = 1;
  int32 nanos = 2;
}
```

取三条包含 `Timestamp` 的消息：

*   `A = {timestamp: {seconds: 100, nanos: 50}}` —— 100.000000050 秒
*   `B = {timestamp: {seconds: 200, nanos: 1}}` —— 200.000000001 秒
*   `C = {timestamp: {seconds: 200, nanos: 0}}` —— 200.000000000 秒

子消息（submessage）按字段逐个递归合并：

*   `A.MergeFrom(B)` 得到 `{seconds: 200, nanos: 1}`。`B` 的两个字段都非零，因此都存在，因此都会覆盖。
*   `A.MergeFrom(C)` 得到 **`{seconds: 200, nanos: 50}`**。`C` 的 `nanos: 0` 与未设置无法区分，因此不会覆盖，`A` 原有的 `nanos: 50` 得以保留。

把时刻 200.000000000 秒合并到 100.000000050 秒之上，得到的是 200.000000050 秒：一个在两个操作数中都不出现的时间戳，偏差了 50 纳秒，而任何地方都不会报错。如果 `Timestamp` 当初是以显式存在性定义的，`C` 就会为 `nanos` 携带一个已置位的位（set bit），合并结果也就会是正确的。

这个问题并非时间戳所特有。任何其含义取决于多个字段组合的消息——一个坐标、一个区间、一个三元版本号、一个比值——都面临同样的风险，而恰恰在零是再普通不过的取值之处，这种风险最为严重。

### MergeFrom(msg) != MergeFrom(bytes)

Protobuf 打算把 `x.MergeFrom(Parse(bytes))` 与 `x.MergeFrom(bytes)` 在语义上等同起来，并将其作为一项重要的一等语义。

隐式存在性是少数违反这一等价性的边缘情况之一：如果字节串中确实含有零值，`Parse(bytes)` 会有效地把它丢弃，随后的合并操作也就不会传播它。相比之下，直接从字节串合并时，这个零值可以被“感知到”，并覆盖一个已经设置的值。

### 补丁语义 {#patch}

同样的规则也破坏了一般意义上的部分更新。如果一个字段是隐式存在性，补丁就无法表达“把这个字段设为零”，因为补丁中的零与省略该字段无法区分。`google.protobuf.FieldMask` 正是为填补这一空缺而生：它是一份带外的、由人工维护的清单，记录调用方想设置的是哪些字段；不过后来人们发现，`FieldMask` 本身还存在其他严重的设计缺陷。

### JSON {#json}

原生 JSON 实现从本质上说就具有显式存在性：解析之后，你就可以检查某个给定的键在线路编码中是否存在。

在 ProtoJSON 中，隐式存在性意味着没有 hazzer：取零值的字段会直接从输出中消失，而且没有简便的办法以某种方式“设置”该字段来表明它应当被输出。唯一可行的补救办法是为序列化器增加“包含默认值”的选项，而这恰恰是我们平时[努力避免](/programming-guides/json#json-options)的那类格式方言开关。显式存在性让这个问题不复存在：设置字段，它就会被输出；清除字段，它就不会被输出。

## 应急出路反而更糟 {#workarounds}

由于真实系统确实需要存在性，proto3 用户当初被引向了 `google.protobuf.Int32Value` 及其同类包装类型、`FieldMask`，以及单字段 `oneof` 块。在每一个重要的维度上，这些方案都比一个 hasbit 更糟：

*   **包装类型（wrapper type）与它们所替代的基本类型字段在线路格式上不兼容**，因此这个决策必须在首次发布之前就做对，而且无法反悔。
*   **包装类型的代价更高**，它把位向量（bitvector）中的一个位变成了一个嵌套子消息，后者拥有自己的指针、自己的内存分配，还有自己的未知字段集合。
*   **`FieldMask` 把存在性挪出了消息**，转移到一个由应用手工保持同步的并行结构之中。
*   **单字段 `oneof` 块**确实携带存在性，但它们歪曲了模式（schema），在每种语言中生成的 API 都不相同，而且那些 API 一贯比 hazzer 更差。

这些代价并非只停留在理论上。每个包装类型带来的额外内存分配，在实际客户端库中是一个可测量的延迟来源；而[要求把存在性重新加入 proto3 的 GitHub issue](https://github.com/protocolbuffers/protobuf/issues/1606) 则成为了 Protobuf 仓库中评论数最多的 issue。

于是，`optional` 关键字被重新加入 proto3：它在 v3.12.0 中先通过 `--experimental_allow_proto3_optional` 标志被接受，随后版次更是直接把显式存在性定为默认。

+++
title = "扩展声明"
weight = 83
description = "详细介绍扩展声明是什么、为什么需要它们，以及如何使用它们。"
type = "docs"
source_url = "https://protobuf.dev/programming-guides/extension-declarations/"
upstream_commit = "f72a6a648b34e9e098cbce1519bc9c8139105d66"
translated_at = "2026-11-19"
status = "translated"
translator = "agent"
+++

<!--*
# Document freshness: For more information, see go/fresh-source.
freshness: { owner: 'shaod' reviewed: '2026-04-23' }
*-->

## 简介 {#intro}

本页详细介绍扩展声明（extension declaration）是什么、为什么需要它们，以及如何使用它们。

{{% alert title="Note" color="note" %}}
Proto3 不支持扩展（extension），[声明自定义选项](/programming-guides/proto3/#customoptions)的情形除外。不过，proto2 和版次（edition）则完全支持扩展。{{% /alert %}}

如果你需要先了解扩展的基础知识，请阅读这篇[扩展指南](https://protobuf.dev/programming-guides/proto2/#extensions)

## 动机 {#motivation}

扩展声明旨在在普通字段与扩展之间取得一种恰当的折中。与扩展一样，它们避免对字段的消息（message）类型产生依赖，因此在难以或无法剔除未使用消息的环境中，这能带来更精简的构建图（build graph）和更小的二进制文件。与普通字段一样，字段名/字段编号会出现在外层消息中，这更便于避免冲突，也便于直观地查看已声明了哪些字段。

通过扩展声明列出已被占用的扩展编号，能让用户更容易挑选一个可用的扩展编号，并避免冲突。

## 用法 {#usage}

扩展声明是扩展范围（extension range）的一种选项。正如 C++ 中的前向声明（forward declaration）一样，你可以在不导入包含完整扩展定义的 `.proto` 文件的情况下，声明某个扩展字段的字段类型、字段名以及基数（cardinality，单数还是 repeated）：

```proto
edition = "2023";

message Foo {
  extensions 4 to 1000 [
    declaration = {
      number: 4,
      full_name: ".my.package.event_annotations",
      type: ".logs.proto.ValidationAnnotations",
      repeated: true },
    declaration = {
      number: 999,
      full_name: ".foo.package.bar",
      type: "int32"}];
}
```

该语法具有以下语义：

*   如果扩展范围的大小允许，可以在单个扩展范围内定义多个使用不同扩展编号的 `declaration`。
*   只要扩展范围存在任何声明，该范围的*所有*扩展也都必须加以声明。这可以防止添加未经声明的扩展，并强制任何新扩展都使用该范围的声明。
*   给定的消息类型（`.logs.proto.ValidationAnnotations`）无需事先定义或导入过。我们只检查它是否为一个有效名称，以及将来是否有可能定义在另一个 `.proto` 文件中。
*   当本文件或其他 `.proto` 文件以该名称或编号定义此消息（`Foo`）的扩展时，我们会强制该扩展的编号、类型和完全限定名与此处前向声明的内容保持一致。

{{% alert title="Warning" color="warning" %}}
避免对诸如 `extensions 4, 999` 这样的扩展范围组使用声明。此时无法确定声明适用于哪个扩展范围，而且这种用法目前不受支持。
{{% /alert %}}

这些扩展声明要求存在两个分别位于不同包（package）中的扩展字段：

```proto
package my.package;
extend Foo {
  repeated logs.proto.ValidationAnnotations event_annotations = 4;
}
```

```proto
package foo.package;
extend Foo {
  optional int32 bar = 999;
}
```

### 保留声明 {#reserved}

扩展声明可以标记为 `reserved: true`，以表明它已不再被实际使用，且对应的扩展定义已被删除。**不要删除该扩展声明，也不要编辑其 `type` 或 `full_name` 值**。

这个 `reserved` 标记与普通字段的 reserved 关键字是相互独立的，并且**不需要拆分扩展范围**。

```proto {highlight="context:reserved"}
edition = "2023";

message Foo {
  extensions 4 to 1000 [
    declaration = {
      number: 500,
      full_name: ".my.package.event_annotations",
      type: ".logs.proto.ValidationAnnotations",
      reserved: true }];
}
```

如果某个扩展字段定义使用了声明中标记为 `reserved` 的编号，它将无法通过编译。

## 在 `descriptor.proto` 中的表示形式 {#representation}

扩展声明在 `descriptor.proto` 中表示为 `proto2.ExtensionRangeOptions` 中的字段：

```proto
message ExtensionRangeOptions {
  message Declaration {
    optional int32 number = 1;
    optional string full_name = 2;
    optional string type = 3;
    optional bool reserved = 5;
    optional bool repeated = 6;
  }
  repeated Declaration declaration = 2;
}
```

## 反射字段查找 {#reflection}

普通的字段查找函数（如 `Descriptor::FindFieldByName()` 或 `Descriptor::FindFieldByNumber()`）*不会*返回扩展声明。与扩展一样，扩展声明可以通过扩展查找例程（如 `DescriptorPool::FindExtensionByName()`）来发现。这是一个明确的设计选择，反映出这样一个事实：声明并非定义，也没有足够的信息来返回完整的 `FieldDescriptor`。

从 TextFormat 和 JSON 的角度来看，已声明的扩展仍然表现得与普通扩展一样。这也意味着，将现有字段迁移为已声明的扩展时，需要先迁移对该字段的所有反射（reflection）式使用。

## 使用扩展声明来分配编号 {#recommendation}

扩展与普通字段一样要使用字段编号，因此为每个扩展分配一个在父消息内唯一的编号非常重要。我们建议使用扩展声明来声明父消息中每个扩展的字段编号和类型。扩展声明充当父消息所有扩展的注册表，protoc 会强制确保不存在字段编号冲突。添加新扩展时，通常只需将上一次添加的扩展编号加一，即可选定下一个可用编号。

**提示：** `MessageSet` 有[专门的指南](#message-set)，其中提供了一个帮助你挑选下一个可用编号的脚本。

每当你删除某个扩展时，请务必将相应字段编号标记为 `reserved`，以消除意外复用该编号的风险。

这项约定只是一种建议——protobuf 团队既没有能力、也没有意愿强迫任何人在每一个可扩展消息上都遵守它。如果你作为可扩展 proto 的所有者，不想通过扩展声明来协调扩展编号，也可以选择通过其他方式进行协调。不过请务必谨慎，因为意外复用扩展编号可能会造成严重的问题。

规避这一问题的一种方法是完全不使用扩展，改用 [`google.protobuf.Any`](/programming-guides/proto3/#any)。对于直接位于存储层之前的 API，或者客户端关心 proto 内容而接收方系统并不关心的透传系统来说，这可能是一个不错的选择。

### 复用扩展编号的后果 {#reusing}

扩展是定义在容器消息之外的字段，通常位于单独的 .proto 文件中。这种定义分散的特点使得两个开发者很容易意外地为同一个扩展字段编号创建不同的定义。

更改扩展定义的后果对扩展和标准字段而言是一样的。复用字段编号会给 proto 应如何从线路格式（wire format）中解码带来歧义。Protobuf 线路格式非常精简，它没有提供很好的方法来检测“使用某个定义编码、却使用另一个定义解码”的字段。

这种歧义可能很快显现，例如使用一个扩展定义的客户端与使用另一个扩展定义的服务端进行通信时。

这种歧义也可能在更长的时间尺度上显现，例如先存储了使用某个扩展定义编码的数据，之后又取出并使用另一个扩展定义来解码。如果第一个扩展定义在数据编码并存储之后已被删除，这种长期情形会很难诊断。

由此导致的后果可能是：

1.  解析错误（最好的情形）。
2.  泄露 PII/SPII（Personally Identifiable Information / Sensitive PII）——如果写入时使用一个扩展定义，而读取时使用另一个扩展定义。
3.  数据损坏——如果使用“错误的”定义读取数据、进行修改后再写回。

数据定义的歧义几乎必然会让某个人至少付出调试的时间。它还可能导致数据泄露或损坏，而清理起来可能需要数月之久。

## 使用提示

### 绝不删除扩展声明 {#never-delete}

删除扩展声明会为将来意外复用敞开大门。如果某个扩展已不再被处理、其定义也已被删除，则可以将相应的扩展声明[标记为保留（reserved）](#reserved)。

### 绝不将 `reserved` 列表中的字段名或字段编号用于新的扩展声明 {#never-reuse-reserved}

保留编号在过去可能已经被用于某些字段或其他扩展。

不建议使用保留字段的 `full_name`，因为在使用 textproto 时可能产生歧义。

### 绝不更改现有扩展声明的类型 {#never-change-type}

更改扩展字段的类型可能导致数据损坏。

如果扩展字段的类型是枚举（enum）或消息类型，而该枚举或消息类型正被重命名，那么更新声明中的名称既是必要的，也是安全的。为避免造成破坏，类型、扩展字段定义和扩展声明的更新应当在同一个提交（commit）中完成。

### 重命名扩展字段时务必谨慎 {#caution-renaming}

重命名扩展字段虽然对线路格式没有影响，但可能会破坏 JSON 和 TextFormat 的解析。

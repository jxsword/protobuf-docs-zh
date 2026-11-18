+++
title = "Go 大小语义"
weight = 630
linkTitle = "大小语义"
description = "解释应如何（以及不应如何）使用 proto.Size"
type = "docs"
source_url = "https://protobuf.dev/reference/go/size/"
upstream_commit = "f72a6a648b34e9e098cbce1519bc9c8139105d66"
translated_at = "2026-11-19"
status = "translated"
translator = "agent"
+++

[`proto.Size`](https://pkg.go.dev/google.golang.org/protobuf/proto#Size) 函数通过遍历一个消息（message）的所有字段（field）——包括子消息（submessage）——返回该 `proto.Message` 以线路格式（wire format）编码（encoding）后的大小（以字节为单位）。

特别需要指出的是，它返回的是 **Go Protobuf 将会怎样编码这条消息**所对应的大小。

## 关于 Protobuf 版次的说明

在 Protobuf 版次（edition）下，`.proto` 文件可以启用会改变序列化（serialization）行为的特性（feature）。这会影响 `proto.Size` 返回的值。例如，设置 `features.field_presence = IMPLICIT` 会使被设置成默认值的标量（scalar）字段不再被序列化，因此也不会计入消息的大小。

## 典型用法

### 识别空消息

检查 [`proto.Size`](https://pkg.go.dev/google.golang.org/protobuf/proto#Size) 是否返回 0，是判断消息是否为空的常用方法：

```go
if proto.Size(m) == 0 {
    // 未设置任何字段；跳过对该消息的处理，
    // 或者返回一个错误，或执行类似操作。
}
```

### 限制程序输出的大小

假设你正在编写一个批处理流水线，它为另一个系统生成工作任务（work task），在本例中我们把那个系统称为“下游系统（downstream system）”。下游系统的资源配置只够处理中小型任务，但负载测试表明，一旦收到超过 500 MB 的工作任务，该系统就会陷入级联故障（cascading failure）。

最好的解决办法是为下游系统添加保护（参见 https://cloud.google.com/blog/products/gcp/using-load-shedding-to-survive-a-success-disaster-cre-life-lessons），但如果实现负载卸载（load-shedding）并不可行，你可以选择在流水线中添加一个快速补救措施：

```go {highlight="context:1,proto.Size,1"}
func (*beamFn) ProcessElement(key string, value []byte, emit func(proto.Message)) {
  task := produceWorkTask(value)
  if proto.Size(task) > 500 * 1024 * 1024 {
    // 跳过每一个超过 500 MB 的工作任务，
    // 以免压垮这个脆弱的下游系统。
    return
  }
  emit(task)
}
```

## 错误用法：与反序列化（Unmarshal）无关

由于 [`proto.Size`](https://pkg.go.dev/google.golang.org/protobuf/proto#Size) 返回的是 Go Protobuf 将会怎样编码该消息的字节数，因此当反序列化（unmarshal，即解码）传入的 Protobuf 消息流时，使用 `proto.Size` 并不安全：

```go {highlight="context:1,proto.Size,1"}
func bytesToSubscriptionList(data []byte) ([]*vpb.EventSubscription, error) {
    subList := []*vpb.EventSubscription{}
    for len(data) > 0 {
        subscription := &vpb.EventSubscription{}
        if err := proto.Unmarshal(data, subscription); err != nil {
            return nil, err
        }
        subList = append(subList, subscription)
        data = data[:len(data)-proto.Size(subscription)]
    }
    return subList, nil
}
```

当 `data` 中包含[非最小线路格式（non-minimal wire format）](#non-minimal)的消息时，`proto.Size` 返回的大小可能与实际被反序列化的字节数不一致，从而导致解析（parse）错误（最好的情况），最坏的情况下则会解析出错误的数据。

因此，只有当所有输入消息都由 Go Protobuf 的同一个版本（version）生成时，这个示例才能可靠地工作。这一点令人意外，而且很可能并非有意为之。

**提示：**请改用 [`protodelim` 包](https://pkg.go.dev/google.golang.org/protobuf/encoding/protodelim)来读写以大小定界的 Protobuf 消息流。

## 高级用法：预先设定缓冲区大小

[`proto.Size`](https://pkg.go.dev/google.golang.org/protobuf/proto#Size) 的一个高级用法，是在序列化之前确定缓冲区所需的大小：

```go
opts := proto.MarshalOptions{
    // 尽可能避免在 Marshal 自身中额外执行一次 proto.Size（参见文档）：
    UseCachedSize: true,
}
// 在实现这一优化机会之前，请勿提交代码（DO NOT SUBMIT）：
// 不要自行分配内存，而是从池中获取一个大小足够的缓冲区。
// 知道了缓冲区的大小，就意味着我们可以把离群值
// 从池中剔除，以防长期运行的远程过程调用（RPC）服务
// 出现不受控的内存增长。
buf := make([]byte, 0, opts.Size(m))
var err error
buf, err = opts.MarshalAppend(buf, m) // 不会产生内存分配
// 注意：len(buf) 可能小于 cap(buf)！请继续阅读下文：
```

请注意，当惰性解码（lazy decoding）被启用时，`proto.Size` 返回的字节数可能多于 `proto.Marshal`（以及 `proto.MarshalAppend` 等变体）实际写入的字节数！因此，当你把编码后的字节发送到线路上（或写入磁盘）时，务必以 `len(buf)` 为准，并丢弃此前得到的任何 `proto.Size` 结果。

具体来说，在 `proto.Size` 与 `proto.Marshal` 之间，一个（子）消息可能发生“缩小”（shrink），条件是：

1.  启用了惰性解码
2.  并且该消息以[非最小线路格式](#non-minimal)抵达
3.  并且在调用 `proto.Size` 之前从未访问过该消息，也就是说它尚未被解码
4.  并且该消息在 `proto.Size` 之后（但在 `proto.Marshal` 之前）被访问，从而触发惰性解码

这种解码会导致后续任何 `proto.Marshal` 调用都对消息进行真正的编码（而不是仅仅复制其线路格式），从而使消息被隐式地规范化（normalize）为 Go 编码消息的方式——这种方式目前是最小线路格式（但不要依赖这一点！）。

可以看到，这一场景相当特殊，但尽管如此，**最佳实践仍是将 `proto.Size` 的结果视为上界（upper bound）**，并且永远不要假设该结果与实际编码出的消息大小一致。

## 背景：非最小线路格式 {#non-minimal}

对 Protobuf 消息进行编码时，存在一个*最小线路格式大小*，以及若干更大的*非最小线路格式*——它们解码后得到的是同一个消息。

非最小线路格式有时也被称为“非规范化线路格式（denormalized wire format）”，它指的是诸如以下的场景：非 repeated 字段出现了多次、非最优的可变长度整数（varint）编码、在线路上呈现为非 packed 形式的 packed 可重复字段，等等。

我们可能在不同的场景下遇到非最小线路格式：

*   **有意为之。**Protobuf 支持通过拼接各自的线路格式来拼接消息。
*   **无意造成。**某个（可能是第三方的）Protobuf 编码器未能理想地编码（例如在编码 varint 时占用了超过必要的空间）。
*   **恶意构造。**攻击者可以专门构造 Protobuf 消息，以通过网络触发崩溃。

+++
title = "Go Opaque API：手动迁移"
weight = 660
linkTitle = "Opaque API：手动迁移"
description = "描述向 Opaque API 的手动迁移。"
type = "docs"
source_url = "https://protobuf.dev/reference/go/opaque-migration-manual/"
upstream_commit = "f72a6a648b34e9e098cbce1519bc9c8139105d66"
translated_at = "2026-11-19"
status = "translated"
translator = "agent"
+++

Opaque API 是面向 Go 编程语言的 Protobuf 实现的最新版本（version）。旧版本现在称为 Open Struct API。简介请参阅博文 [Go Protobuf：发布 Opaque API](https://go.dev/blog/protobuf-opaque)。

本指南面向用户，介绍如何将 Go Protobuf 的使用方式从较旧的 Open Struct API 迁移到新的 Opaque API。

{{% alert title="Warning" color="warning" %}}你正在查看的是手动迁移指南。通常情况下，更好的做法是使用 `open2opaque` 工具来自动化迁移。请改为参阅 [Opaque API 迁移](/reference/go/opaque-migration)。 {{% /alert %}}

[生成代码指南（Generated Code Guide）](/reference/go/go-generated-opaque)提供了更多细节。本指南将新旧 API 并排对比。

### 消息构造

假设有一个如下定义的 Protobuf 消息（message）：

```proto
message Foo {
  uint32 uint32 = 1;
  bytes bytes = 2;
  oneof union {
    string    string = 4;
    MyMessage message = 5;
  }
  enum Kind { … };
  Kind kind = 9;
}
```

下面是从字面值构造该消息的示例：

<table width="100%">
        <tr>
                <td width="50%">Open Struct API（旧）</td>
                <td width="50%">Opaque API（新）</td>
        </tr>
<tr>
<td>

```go
m := &pb.Foo{
  Uint32: proto.Uint32(5),
  Bytes:  []byte("hello"),
}
```

</td>
<td>

```go
m := pb.Foo_builder{
  Uint32: proto.Uint32(5),
  Bytes:  []byte("hello"),
}.Build()
```

</td>
</tr>
</table>

如你所见，构建器（builder）结构体使 Open Struct API（旧）与 Opaque API（新）之间几乎可以做到 1:1 的转换。

一般而言，为了可读性，应优先使用构建器。只有在极少数情况下，例如在内层热循环中创建 Protobuf 消息时，使用 setter 才可能比构建器更合适。更多细节请参阅 [Opaque API FAQ：应该使用构建器还是 setter？](/reference/go/opaque-faq#builders-vs-setters)。

上述示例有一个例外，就是在使用 [oneof](#oneofs) 时：Open Struct API（旧）为每个 oneof case 使用一个包装结构体类型（wrapper struct type），而 Opaque API（新）则将 oneof 字段（field）当作普通消息字段来处理：

<table width="100%">
        <tr>
                <td width="50%">Open Struct API（旧）</td>
                <td width="50%">Opaque API（新）</td>
        </tr>
<tr>
<td>

```go
m := &pb.Foo{
  Uint32: myScalar,  // 可能为 nil
  Union:  &pb.Foo_String{myString},
  Kind:   pb.Foo_SPECIAL_KIND.Enum(),
}
```

</td>
<td>

```go
m := pb.Foo_builder{
  Uint32: myScalar,
  String: myString,
  Kind:   pb.Foo_SPECIAL_KIND.Enum(),
}.Build()
```

</td>
</tr>
</table>

对于与某个 oneof union 相关联的那组 Go 结构体字段，一次只能填充其中一个字段。如果填充了多个 oneof case 字段，则以最后一个为准（按 .proto 文件中的字段声明顺序）。

### 标量字段

假设有一个定义了标量（scalar）字段的消息：

```proto
message Artist {
  int32 birth_year = 1;
}
```

Go 使用标量类型（bool、int32、int64、uint32、uint64、float32、float64、string、[]byte 以及枚举（enum））的 Protobuf 消息字段将拥有 `Get` 和 `Set` 访问器（accessor）方法。具有[显式存在性（explicit presence）](/programming-guides/field_presence/)的字段还将拥有 `Has` 和 `Clear` 方法。

对于类型为 `int32`、名为 `birth_year` 的字段，将为其生成以下访问器方法：

```go
func (m *Artist) GetBirthYear() int32
func (m *Artist) SetBirthYear(v int32)
func (m *Artist) HasBirthYear() bool
func (m *Artist) ClearBirthYear()
```

`Get` 返回该字段的值。如果字段未设置或消息接收者为 nil，则返回默认值（default value）。默认值是 [零值（zero value）](https://go.dev/ref/spec#The_zero_value)，除非已通过 default 选项（option）显式设置。

`Set` 将提供的值存入该字段。在 nil 消息接收者上调用时会 panic。

对于 bytes 字段，使用 nil []byte 调用 `Set` 也会被视为已设置。例如，紧接着调用 `Has` 会返回 true；紧接着调用 `Get` 会返回零长度的切片（既可能是 nil，也可能是空切片）。用户应使用 `Has` 来判断存在性，而不应依赖 `Get` 是否返回 nil。

`Has` 报告字段是否已填充。在 nil 消息接收者上调用时返回 false。

`Clear` 清空该字段。在 nil 消息接收者上调用时会 panic。

**使用字符串字段的示例代码片段：**

<table width="100%">
        <tr>
                <td width="50%">Open Struct API（旧）</td>
                <td width="50%">Opaque API（新）</td>
        </tr>
<tr>
<td>

```go
// 获取值。
s := m.GetBirthYear()

// 设置字段。
m.BirthYear = proto.Int32(1989)

// 检查存在性。
if s.BirthYear != nil { … }

// 清空字段。
m.BirthYear = nil
```

</td>
<td>

```go
// 获取字段值。
s := m.GetBirthYear()

// 设置字段。
m.SetBirthYear(1989)

// 检查存在性。
if m.HasBirthYear() { … }

// 清空字段
m.ClearBirthYear()
```

</td>
</tr>
</table>

### 消息字段

假设有一个定义了消息类型字段的消息：

```proto
message Band {}

message Concert {
  Band headliner = 1;
}
```

类型为消息的 Protobuf 消息字段将拥有 `Get`、`Set`、`Has` 和 `Clear` 方法。

对于名为 `headliner` 的消息类型字段，将为其生成以下访问器方法：

```go
func (m *Concert) GetHeadliner() *Band
func (m *Concert) SetHeadliner(*Band)
func (m *Concert) HasHeadliner() bool
func (m *Concert) ClearHeadliner()
```

`Get` 返回该字段的值。如果未设置或在 nil 消息接收者上调用，则返回 nil。检查 `Get` 是否返回 nil，等价于检查 `Has` 是否返回 false。

`Set` 将提供的值存入该字段。在 nil 消息接收者上调用时会 panic。用 nil 指针调用 `Set` 等价于调用 `Clear`。

`Has` 报告字段是否已填充。在 nil 消息接收者上调用时返回 false。

`Clear` 清空该字段。在 nil 消息接收者上调用时会 panic。

**示例代码片段**

<table width="100%">
        <tr>
                <td width="50%">Open Struct API（旧）</td>
                <td width="50%">Opaque（新）</td>
        </tr>
<tr>
<td>

```go
// 获取值。
b := m.GetHeadliner()

// 设置字段。
m.Headliner = &pb.Band{}

// 检查存在性。
if s.Headliner != nil { … }

// 清空字段。
m.Headliner = nil
```

</td>
<td>

```go
// 获取值。
s := m.GetHeadliner()

// 设置字段。
m.SetHeadliner(&pb.Band{})

// 检查存在性。
if m.HasHeadliner() { … }

// 清空字段
m.ClearHeadliner()
```

</td>
</tr>
</table>

### repeated 字段

假设有一个定义了 repeated 消息类型字段的消息：

```proto
message Concert {
  repeated Band support_acts = 2;
}
```

repeated 字段将拥有 `Get` 和 `Set` 方法。

`Get` 返回该字段的值。如果字段未设置或消息接收者为 nil，则返回 nil。

`Set` 将提供的值存入该字段。在 nil 消息接收者上调用时会 panic。`Set` 会存储所提供切片头（slice header）的副本。对切片内容的修改在 repeated 字段中是可见的。因此，如果用空切片调用 `Set`，紧接着调用 `Get` 将返回同一个切片。对于线路格式（wire format）或文本格式的序列化输出，传入的 nil 切片与空切片不可区分。

对于消息 `Concert` 上名为 `support_acts` 的 repeated 消息类型字段，将为其生成以下访问器方法：

```go
func (m *Concert) GetSupportActs() []*Band
func (m *Concert) SetSupportActs([]*Band)
```

**示例代码片段**

<table width="100%">
        <tr>
                <td width="50%">Open Struct API（旧）</td>
                <td width="50%">Opaque API（新）</td>
        </tr>
<tr>
<td>

```go
// 获取整个 repeated 值。
v := m.GetSupportActs()

// 设置字段。
m.SupportActs = v

// 获取 repeated 字段中的一个元素。
e := m.SupportActs[i]

// 设置 repeated 字段中的一个元素。
m.SupportActs[i] = e

// 获取 repeated 字段的长度。
n := len(m.GetSupportActs())

// 截断 repeated 字段。
m.SupportActs = m.SupportActs[:i]

// 追加到 repeated 字段。
m.SupportActs = append(m.GetSupportActs(), e)
m.SupportActs = append(m.GetSupportActs(), v...)

// 清空字段。
m.SupportActs = nil
```

</td>
<td>

```go
// 获取整个 repeated 值。
v := m.GetSupportActs()

// 设置字段。
m.SetSupportActs(v)

// 获取 repeated 字段中的一个元素。
e := m.GetSupportActs()[i]

// 设置 repeated 字段中的一个元素。
m.GetSupportActs()[i] = e

// 获取 repeated 字段的长度。
n := len(m.GetSupportActs())

// 截断 repeated 字段。
m.SetSupportActs(m.GetSupportActs()[:i])

// 追加到 repeated 字段。
m.SetSupportActs(append(m.GetSupportActs(), e))
m.SetSupportActs(append(m.GetSupportActs(), v...))

// 清空字段。
m.SetSupportActs(nil)
```

</td>
</tr>
</table>

### map

假设有一个定义了 map 类型字段的消息：

```proto
message MerchBooth {
  map<string, MerchItems> items = 1;
}
```

map 字段将拥有 `Get` 和 `Set` 方法。

`Get` 返回该字段的值。如果字段未设置或消息接收者为 nil，则返回 nil。

`Set` 将提供的值存入该字段。在 nil 消息接收者上调用时会 panic。`Set` 会存储所提供 map 引用的副本。对所提供 map 的修改在 map 字段中是可见的。

对于消息 `MerchBooth` 上名为 `items` 的 map 字段，将为其生成以下访问器方法：

```go
func (m *MerchBooth) GetItems() map[string]*MerchItem
func (m *MerchBooth) SetItems(map[string]*MerchItem)
```

**示例代码片段**

<table width="100%">
        <tr>
                <td width="50%">Open Struct API（旧）</td>
                <td width="50%">Opaque API（新）</td>
        </tr>
<tr>
<td>

```go
// 获取整个 map 值。
v := m.GetItems()

// 设置字段。
m.Items = v

// 获取 map 字段中的一个元素。
v := m.Items[k]

// 设置 map 字段中的一个元素。
// 如果 m.Items 为 nil，这里会 panic。
// 你应当在赋值之前检查 m.Items 是否为 nil，
// 以确保这次赋值
// 不会 panic。
m.Items[k] = v

// 删除 map 字段中的一个元素。
delete(m.Items, k)

// 获取 map 字段的大小。
n := len(m.GetItems())

// 清空字段。
m.Items = nil
```

</td>
<td>

```go
// 获取整个 map 值。
v := m.GetItems()

// 设置字段。
m.SetItems(v)

// 获取 map 字段中的一个元素。
v := m.GetItems()[k]

// 设置 map 字段中的一个元素。
// 如果 m.GetItems() 为 nil，这里会 panic。
// 你应当在赋值之前检查 m.GetItems() 是否为 nil，
// 以确保这次赋值
// 不会 panic。
m.GetItems()[k] = v

// 删除 map 字段中的一个元素。
delete(m.GetItems(), k)

// 获取 map 字段的大小。
n := len(m.GetItems())

// 清空字段。
m.SetItems(nil)
```

</td>
</tr>
</table>

### oneof

对于每个 oneof union 分组，消息上将有 `Which`、`Has` 和 `Clear` 方法。该 union 中的每个 oneof case 字段上也将有 `Get`、`Set`、`Has` 和 `Clear` 方法。

假设有一个消息，其在 oneof `avatar` 中定义了 oneof 字段 `image_url` 和 `image_data`，如下：

```proto
message Profile {
  oneof avatar {
    string image_url = 1;
    bytes image_data = 2;
  }
}
```

为该 oneof 生成的 Opaque API 将是：

```go
func (m *Profile) WhichAvatar() case_Profile_Avatar { … }
func (m *Profile) HasAvatar() bool { … }
func (m *Profile) ClearAvatar() { … }

type case_Profile_Avatar protoreflect.FieldNumber

const (
  Profile_Avatar_not_set_case case_Profile_Avatar = 0
  Profile_ImageUrl_case case_Profile_Avatar = 1
  Profile_ImageData_case case_Profile_Avatar = 2
)
```

`Which` 通过返回字段编号（field number）来报告当前设置的是哪个 case 字段。当没有任何字段被设置或在 nil 消息接收者上调用时，返回 0。

`Has` 报告 oneof 中是否有任一字段被设置。在 nil 消息接收者上调用时返回 false。

`Clear` 清空 oneof 中当前已设置的 case 字段。在 nil 消息接收者上调用时会 panic。

为每个 oneof case 字段生成的 Opaque API 将是：

```go
func (m *Profile) GetImageUrl() string { … }
func (m *Profile) GetImageData() []byte { … }

func (m *Profile) SetImageUrl(v string) { … }
func (m *Profile) SetImageData(v []byte) { … }

func (m *Profile) HasImageUrl() bool { … }
func (m *Profile) HasImageData() bool { … }

func (m *Profile) ClearImageUrl() { … }
func (m *Profile) ClearImageData() { … }
```

`Get` 返回该 case 字段的值。如果该 case 字段未设置或在 nil 消息接收者上调用，将返回零值。

`Set` 将提供的值存入该 case 字段。它还会隐式清空该 oneof union 中先前被填充的 case 字段。对 oneof 消息 case 字段以 nil 值调用 `Set`（即向 `Set` 传入 nil），会将该字段设置为一个空消息。在 nil 消息接收者上调用时会 panic。

`Has` 报告该 case 字段是否已被设置。在 nil 消息接收者上调用时返回 false。

`Clear` 清空该 case 字段。如果它先前已被设置，oneof union 也会随之被清空。如果 oneof union 已被设置为另一个字段，则不会清空该 oneof union。在 nil 消息接收者上调用时会 panic。

**示例代码片段**

<table width="100%">
        <tr>
                <td width="50%">Open Struct API（旧）</td>
                <td width="50%">Opaque API（新）</td>
        </tr>
<tr>
<td>

```go
// 获取已设置的 oneof 字段。
switch m.GetAvatar().(type) {
case *pb.Profile_ImageUrl:
  … = m.GetImageUrl()
case *pb.Profile_ImageData:
  … = m.GetImageData()
}

// 设置字段。
m.Avatar = &pb.Profile_ImageUrl{"http://"}
m.Avatar = &pb.Profile_ImageData{img}

// 检查是否有任一 oneof 字段被设置
if m.Avatar != nil { … }

// 清空字段。
m.Avatar = nil

// 检查某个特定字段是否被设置。
_, ok := m.GetAvatar().(*pb.Profile_ImageUrl)
if ok { … }

// 清空某个特定字段
_, ok := m.GetAvatar().(*pb.Profile_ImageUrl)
if ok {
  m.Avatar = nil
}

// 复制一个 oneof 字段。
m.Avatar = src.Avatar
```

</td>
<td>

```go
// 获取已设置的 oneof 字段。
switch m.WhichAvatar() {
case pb.Profile_ImageUrl_case:
  … = m.GetImageUrl()
case pb.Profile_ImageData_case:
  … = m.GetImageData()
}

// 设置字段。
m.SetImageUrl("http://")
m.SetImageData([]byte("…"))

// 检查是否有任一 oneof 字段被设置
if m.HasAvatar() { … }

// 清空字段。
m.ClearAvatar()

// 检查某个特定字段是否被设置。
if m.HasImageUrl() { … }

// 清空某个特定字段。
m.ClearImageUrl()

// 复制一个 oneof 字段
switch src.WhichAvatar() {
case pb.Profile_ImageUrl_case:
  m.SetImageUrl(src.GetImageUrl())
case pb.Profile_ImageData_case:
  m.SetImageData(src.GetImageData())
}
```

</td>
</tr>

</table>

### 反射（reflection）

对 proto 消息类型使用 Go `reflect` 包来访问结构体字段和标签（tag）的代码，在脱离 Open Struct API 迁移后将无法继续工作。这类代码需要迁移为使用 [protoreflect](https://pkg.go.dev/google.golang.org/protobuf/reflect/protoreflect)。

一些常用库在底层确实用到了 Go `reflect`，例如：

*   [`encoding/json`](https://pkg.go.dev/encoding/json/)
    *   请改用
        [`protobuf/encoding/protojson`](https://pkg.go.dev/google.golang.org/protobuf/encoding/protojson)。
*   [`pretty`](https://pkg.go.dev/github.com/kr/pretty)
*   [`cmp`](https://pkg.go.dev/github.com/google/go-cmp/cmp)
    *   要在 Protobuf 消息上正确使用 `cmp.Equal`，请配合使用
        [protocmp.Transform](https://pkg.go.dev/google.golang.org/protobuf/testing/protocmp#Transform)

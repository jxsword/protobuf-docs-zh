+++
title = "Go 生成代码指南（不透明）"
weight = 615
linkTitle = "生成代码指南（不透明）"
description = "确切描述 Protobuf 编译器为任意给定的协议定义所生成的 Go 代码。"
type = "docs"
source_url = "https://protobuf.dev/reference/go/go-generated-opaque/"
upstream_commit = "f72a6a648b34e9e098cbce1519bc9c8139105d66"
translated_at = "2026-11-19"
status = "translated"
translator = "agent"
+++

proto2 与 proto3 生成代码（generated code）之间的任何差异都会以高亮形式标出——请注意，这些差异存在于本文所描述的生成代码中，而非基础 API；基础 API 在两个版本中是相同的。在阅读本文之前，你应该先阅读 [proto2 语言指南（language guide）](/programming-guides/proto2) 和/或 [proto3 语言指南](/programming-guides/proto3)。

{{% alert title="Note" color="warning" %}}你正在阅读的是 Opaque API（当前版本）的文档。如果你处理的 `.proto` 文件使用的是旧版 Open Struct API（可以从相应 `.proto` 文件中的 API level 设置判断出来），请参阅 [Go 生成代码（开放）](/reference/go/go-generated) 获取对应的文档。Opaque API 的介绍请参阅博文 [Go Protobuf: The new Opaque API](https://go.dev/blog/protobuf-opaque)。 {{% /alert %}}

## 编译器调用 {#invocation}

Protobuf 编译器需要一个插件（plugin）来生成 Go 代码。请使用 Go 1.16 或更高版本，运行以下命令进行安装：

```shell
go install google.golang.org/protobuf/cmd/protoc-gen-go@latest
```

这会在 `$GOBIN` 中安装一个 `protoc-gen-go` 二进制文件。你可以设置 `$GOBIN` 环境变量来更改安装位置。Protobuf 编译器要能找到它，该路径必须位于你的 `$PATH` 中。

使用 `go_out` 标志调用 Protobuf 编译器时，它会生成 Go 输出。`go_out` 标志的参数是你希望编译器写入 Go 输出的目录。编译器会为每个输入的 `.proto` 文件创建一个源文件，输出文件名是通过把 `.proto` 扩展名替换为 `.pb.go` 得到的。

生成的 `.pb.go` 文件在输出目录中的具体位置取决于编译器标志。有几种输出模式：

-   如果指定了 `paths=import` 标志，输出文件会被放置在以 Go 包的导入路径命名的目录中（例如由 `.proto` 文件中的 `go_package` 选项提供的导入路径）。例如，输入文件 `protos/buzz.proto` 的 Go 导入路径为 `example.com/project/protos/fizz`，则输出文件位于 `example.com/project/protos/fizz/buzz.pb.go`。如果未指定 `paths` 标志，这就是默认的输出模式。
-   如果指定了 `module=$PREFIX` 标志，输出文件会被放置在以 Go 包的导入路径命名的目录中（例如由 `.proto` 文件中的 `go_package` 选项提供的导入路径），但会从输出文件名中去除指定的目录前缀。例如，输入文件 `protos/buzz.proto` 的 Go 导入路径为 `example.com/project/protos/fizz`，并且指定 `example.com/project` 作为 `module` 前缀，则输出文件位于 `protos/fizz/buzz.pb.go`。如果在模块路径之外生成任何 Go 包，都会导致错误。这种模式适合把生成的文件直接输出到 Go 模块中。
-   如果指定了 `paths=source_relative` 标志，输出文件会被放置在与输入文件相同的相对目录中。例如，输入文件 `protos/buzz.proto` 的输出文件位于 `protos/buzz.pb.go`。

通过在调用 `protoc` 时传入 `go_opt` 标志，可以提供 `protoc-gen-go` 专有的标志。可以传入多个 `go_opt` 标志。例如，运行以下命令时：

```shell
protoc --proto_path=src --go_out=out --go_opt=paths=source_relative foo.proto bar/baz.proto
```

编译器会从 `src` 目录中读取输入文件 `foo.proto` 和 `bar/baz.proto`，并把输出文件 `foo.pb.go` 和 `bar/baz.pb.go` 写入 `out` 目录。编译器会在必要时自动创建嵌套的输出子目录，但不会创建输出目录本身。

## 包 {#package}

要生成 Go 代码，必须为每个 `.proto` 文件（包括被生成的 `.proto` 文件所间接依赖的文件）提供其 Go 包的导入路径。指定 Go 导入路径有两种方式：

-   在 `.proto` 文件中声明；或者
-   在调用 `protoc` 时在命令行上声明。

我们建议在 `.proto` 文件中声明，这样 `.proto` 文件对应的 Go 包就能随 `.proto` 文件本身集中标识，同时还能简化调用 `protoc` 时传入的标志集合。如果某个 `.proto` 文件的 Go 导入路径既在 `.proto` 文件本身中提供，又在命令行上提供，则后者优先于前者。

在 `.proto` 文件内部，可以通过声明带 Go 包完整导入路径的 `go_package` 选项来局部指定 Go 导入路径。用法示例：

```proto
option go_package = "example.com/project/protos/fizz";
```

也可以在调用编译器时，通过在命令行上传入一个或多个 `M${PROTO_FILE}=${GO_IMPORT_PATH}` 标志来指定 Go 导入路径。用法示例：

```shell
protoc --proto_path=src \
  --go_opt=Mprotos/buzz.proto=example.com/project/protos/fizz \
  --go_opt=Mprotos/bar.proto=example.com/project/protos/foo \
  protos/buzz.proto protos/bar.proto
```

由于所有 `.proto` 文件到其 Go 导入路径的映射可能非常庞大，这种指定 Go 导入路径的方式通常由能够控制整个依赖树的构建工具（例如 [Bazel](https://bazel.build/)）来完成。如果某个 `.proto` 文件存在重复的映射条目，则以最后指定的为准。

对于 `go_package` 选项和 `M` 标志，其值（value）都可以包含一个显式的包名，包名与导入路径之间用分号分隔，例如：“example.com/protos/foo;package_name”。不推荐这种用法，因为默认情况下包名会以合理的方式从导入路径推导而来。

当一个 `.proto` 文件导入另一个 `.proto` 文件时，导入路径用于确定必须生成哪些 import 语句。例如，如果 `a.proto` 导入了 `b.proto`，那么生成的 `a.pb.go` 文件就需要导入包含所生成的 `b.pb.go` 文件的 Go 包（除非这两个文件位于同一个包中）。导入路径还用于构造输出文件名。详情请参阅上文的“编译器调用”一节。

Go 导入路径与 `.proto` 文件中的 [`package` 指示符](/programming-guides/proto3#packages)之间没有任何关联：后者只与 Protobuf 命名空间（namespace）相关，而前者只与 Go 命名空间相关。同样，Go 导入路径与 `.proto` 导入路径之间也没有关联。

## API 级别 {#apilevel}

生成的代码要么使用 Open Struct API，要么使用 Opaque API。简介请参阅博文 [Go Protobuf: The new Opaque API](https://go.dev/blog/protobuf-opaque)。

根据你的 `.proto` 文件所使用的语法，将会采用以下 API：

`.proto` 语法    | API 级别
---------------- | ----------
proto2           | Open Struct API
proto3           | Open Struct API
版次 2023        | Open Struct API
版次 2024+       | Opaque API

你可以在 `.proto` 文件中设置 `api_level` 这个版次特性（feature）来选择 API。它既可以按文件设置，也可以按消息（message）设置：

```proto
edition = "2023";

package log;

import "google/protobuf/go_features.proto";
option features.(pb.go).api_level = API_OPAQUE;

message LogEntry { … }
```

为方便起见，你也可以用 `protoc` 命令行标志来覆盖默认的 API 级别：

```
protoc […] --go_opt=default_api_level=API_HYBRID
```

要针对某个特定文件（而非所有文件）覆盖默认的 API 级别，请使用 `apilevelM` 映射标志（类似于[用于导入路径的 `M` 标志](#package)）：

```
protoc […] --go_opt=apilevelMhello.proto=API_HYBRID
```

这些命令行标志对仍在使用 proto2 或 proto3 语法的 `.proto` 文件同样有效；但如果你想从 `.proto` 文件内部选择 API 级别，则需要先把该文件迁移到版次（editions）。

## 消息 {#message}

给定一个简单的消息声明：

```proto
message Artist {}
```

Protobuf 编译器会生成一个名为 `Artist` 的结构体。`*Artist` 实现了 [`proto.Message`](https://pkg.go.dev/google.golang.org/protobuf/proto?tab=doc#Message) 接口。

[`proto` 包](https://pkg.go.dev/google.golang.org/protobuf/proto?tab=doc)提供了操作消息的函数，包括与二进制格式（binary format）之间的相互转换。

`proto.Message` 接口定义了一个 `ProtoReflect` 方法。该方法返回一个 [`protoreflect.Message`](https://pkg.go.dev/google.golang.org/protobuf/reflect/protoreflect?tab=doc#Message)，它提供了消息的基于反射（reflection）的视图。

`optimize_for` 选项不影响 Go 代码生成器（code generator）的输出。

当多个 goroutine 并发访问同一个消息时，适用以下规则：

*   并发访问（读取）字段是安全的，但有一个例外：
    *   首次访问[惰性字段（lazy field）](https://github.com/protocolbuffers/protobuf/blob/cacb096002994000f8ccc6d9b8e1b5b0783ee561/src/google/protobuf/descriptor.proto#L609)属于一次修改。
*   在同一个消息中修改不同的字段是安全的。
*   并发修改同一个字段是不安全的。
*   在以任何方式修改消息的同时，并发调用 [`proto` 包](https://pkg.go.dev/google.golang.org/protobuf/proto?tab=doc)的函数（例如 [`proto.Marshal`](https://pkg.go.dev/google.golang.org/protobuf/proto#Marshal) 或 [`proto.Size`](https://pkg.go.dev/google.golang.org/protobuf/proto#Size)）是不安全的。

### 嵌套类型

消息可以声明在另一个消息内部。例如：

```proto
message Artist {
  message Name {
  }
}
```

在这种情况下，编译器会生成两个结构体：`Artist` 和 `Artist_Name`。

## 字段

Protobuf 编译器会为消息中定义的每个字段生成访问器方法（accessor method，即 setter 和 getter）。

请注意，生成的 Go 访问器方法一律采用驼峰式命名，即使 `.proto` 文件中的字段名（field name）使用的是带下划线的小写形式（[正如样式指南所要求的那样](/programming-guides/style)）。大小写转换规则如下：

1.  首字母大写以便导出。如果第一个字符是下划线，则将其移除，并在前面加上大写的 X。
2.  如果内部的下划线后面跟着小写字母，则移除该下划线，并将后面的字母大写。

因此，在 Go 中你可以使用 `GetBirthYear()` 方法访问 proto 字段 `birth_year`，使用 `GetXBirthYear_2()` 访问 `_birth_year_2`。

### 单数字段

对于这个字段定义：

```proto
// proto2 和 proto3
message Artist {
  optional int32 birth_year = 1;
}

// 版次（editions）
message Artist {
  int32 birth_year = 1 [features.field_presence = EXPLICIT];
}
```

编译器会生成一个带有以下访问器方法的 Go 结构体：

```go
func (m *Artist) GetBirthYear() int32
func (m *Artist) SetBirthYear(v int32)
```

对于隐式存在性（implicit presence），getter 返回 `birth_year` 中的 `int32` 值；如果字段未设置，则返回该类型的[零值（zero value）](https://golang.org/ref/spec#The_zero_value)（数字为 `0`，字符串为空字符串）。对于显式存在性（explicit presence），getter 返回 `birth_year` 中的 `int32` 值；如果字段未设置，则返回默认值（default value）。如果没有显式设置默认值，则改用零值。

对于其他标量（scalar）字段类型（包括 `bool`、`bytes` 和 `string`），`int32` 会按照[标量值类型表](/programming-guides/proto3#scalar)替换为相应的 Go 类型。

在具有显式存在性的字段上，你还可以使用以下方法：

```go
func (m *Artist) HasBirthYear() bool
func (m *Artist) ClearBirthYear()
```

### 单数消息字段 {#singular-message}

给定消息类型：

```proto
message Band {}
```

对于带有 `Band` 字段的消息：

```proto
// proto2
message Concert {
  optional Band headliner = 1;
  // 如果使用 required 而非 optional，生成的代码结果相同。
}

// proto3 和版次
message Concert {
  Band headliner = 1;
}
```

编译器会生成一个带有以下访问器方法的 Go 结构体：

```go
type Concert struct { ... }

func (m *Concert) GetHeadliner() *Band { ... }
func (m *Concert) SetHeadliner(v *Band) { ... }
func (m *Concert) HasHeadliner() bool { ... }
func (m *Concert) ClearHeadliner() { ... }
```

即使 `m` 为 nil，调用 `GetHeadliner()` 访问器方法也是安全的。这使得可以在没有中间 `nil` 检查的情况下链式调用 get 方法：

```go
var m *Concert // 默认为 nil
log.Infof("GetFoundingYear() = %d (no panic!)", m.GetHeadliner().GetFoundingYear())
```

如果字段未设置，getter 会返回该字段的默认值。对于消息而言，默认值是 nil 指针。

与 getter 不同，setter 不会替你执行 nil 检查。因此，你不能在可能为 nil 的消息上安全地调用 setter。

### repeated 字段 {#repeated}

对于 repeated 字段，访问器方法使用切片类型。对于这个带有 repeated 字段的消息：

```proto
message Concert {
  // 最佳实践：repeated 字段使用复数名称：
  // /programming-guides/style#repeated-fields
  repeated Band support_acts = 1;
}
```

编译器会生成一个带有以下访问器方法的 Go 结构体：

```go
type Concert struct { ... }

func (m *Concert) GetSupportActs() []*Band { ... }
func (m *Concert) SetSupportActs(v []*Band) { ... }
```

同样，对于字段定义 `repeated bytes band_promo_images = 1;`，编译器会生成操作 `[][]byte` 类型的访问器。对于 repeated 的[枚举](#enum) `repeated MusicGenre genres = 2;`，编译器会生成操作 `[]MusicGenre` 类型的访问器。

下面的示例展示了如何使用[构建器（builder）](#builders)来构造 `Concert` 消息。

```go
concert := Concert_builder{
  SupportActs: []*Band{
    {}, // 第一个元素。
    {}, // 第二个元素。
  },
}.Build()
```

你也可以改用 setter：

```go
concert := &Concert{}
concert.SetSupportActs([]*Band{
    {}, // 第一个元素。
    {}, // 第二个元素。
})
```

要访问该字段，可以这样做：

```go
support := concert.GetSupportActs() // support 的类型是 []*Band。
b1 := support[0] // b1 的类型是 *Band，即 support_acts 中的第一个元素。
```

### map 字段 {#map}

每个 map 字段都会生成操作 `map[TKey]TValue` 类型的访问器，其中 `TKey` 是字段的键（key）类型，`TValue` 是字段的值类型。对于这个带有 map 字段的消息：

```proto
message MerchItem {}

message MerchBooth {
  // items 将商品名称（"Signed T-Shirt"）映射到
  // 包含该商品更多详情的 MerchItem 消息。
  map<string, MerchItem> items = 1;
}
```

编译器会生成一个带有以下访问器方法的 Go 结构体：

```go
type MerchBooth struct { ... }

func (m *MerchBooth) GetItems() map[string]*MerchItem { ... }
func (m *MerchBooth) SetItems(v map[string]*MerchItem) { ... }
```

### oneof 字段 {#oneof}

对于 oneof 字段，Protobuf 编译器会为 oneof 中的每个[单数字段](#singular-scalar-proto2)生成访问器。

对于这个带有 oneof 字段的消息：

```proto
package account;
message Profile {
  oneof avatar {
    string image_url = 1;
    bytes image_data = 2;
  }
}
```

编译器会生成一个带有以下访问器方法的 Go 结构体：

```go
type Profile struct { ... }

func (m *Profile) WhichAvatar() case_Profile_Avatar { ... }
func (m *Profile) GetImageUrl() string { ... }
func (m *Profile) GetImageData() []byte { ... }

func (m *Profile) SetImageUrl(v string) { ... }
func (m *Profile) SetImageData(v []byte) { ... }

func (m *Profile) HasAvatar() bool { ... }
func (m *Profile) HasImageUrl() bool { ... }
func (m *Profile) HasImageData() bool { ... }

func (m *Profile) ClearAvatar() { ... }
func (m *Profile) ClearImageUrl() { ... }
func (m *Profile) ClearImageData() { ... }
```

下面的示例展示了如何使用[构建器](#builders)来设置该字段：

```go
p1 := accountpb.Profile_builder{
  ImageUrl: proto.String("https://example.com/image.png"),
}.Build()
```

……或者等价地，使用 setter：

```go
// imageData 是 []byte 类型
imageData := getImageData()
p2 := &accountpb.Profile{}
p2.SetImageData(imageData)
```

要访问该字段，可以对 `WhichAvatar()` 的结果使用 switch 语句：

```go
switch m.WhichAvatar() {
case accountpb.Profile_ImageUrl_case:
    // 基于 URL 加载头像图片
    // 使用 m.GetImageUrl()

case accountpb.Profile_ImageData_case:
    // 基于字节数据加载头像图片
    // 使用 m.GetImageData()

case accountpb.Profile_Avatar_not_set_case:
    // 该字段未设置。

default:
    return fmt.Errorf("Profile.Avatar has an unexpected new oneof field %v", x)
}
```

### 构建器 {#builders}

构建器是一种在单个表达式中构造并初始化消息的便捷方式，在处理嵌套消息时尤为方便，例如在单元测试中。

与其他语言（如 Java）中的构建器不同，Go Protobuf 的构建器并不适合在函数之间传递。正确做法是立即调用 `Build()`，然后传递得到的 proto 消息，并使用 setter 来修改字段。

下面是使用构建器创建 `Band` 消息的示例，该消息位于外层 `Concert` 消息中唯一的 repeated 字段内：

```go
concert := Concert_builder{
  SupportActs: []*Band{
    Band_builder{
      Name: proto.String("Varint and the Marshals"),
    }.Build()
  },
}.Build()
```

## 枚举 {#enum}

给定如下枚举：

```proto
message Venue {
  enum Kind {
    KIND_UNSPECIFIED = 0;
    KIND_CONCERT_HALL = 1;
    KIND_STADIUM = 2;
    KIND_BAR = 3;
    KIND_OPEN_AIR_FESTIVAL = 4;
  }
  Kind kind = 1;
  // ...
}
```

Protobuf 编译器会生成一个类型以及一系列具有该类型的常量：

```go
type Venue_Kind int32

const (
    Venue_KIND_UNSPECIFIED       Venue_Kind = 0
    Venue_KIND_CONCERT_HALL      Venue_Kind = 1
    Venue_KIND_STADIUM           Venue_Kind = 2
    Venue_KIND_BAR               Venue_Kind = 3
    Venue_KIND_OPEN_AIR_FESTIVAL Venue_Kind = 4
)
```

对于消息内部的枚举（如上例），类型名以消息名开头：

```go
type Venue_Kind int32
```

对于包级别的枚举：

```proto
enum Genre {
  GENRE_UNSPECIFIED = 0;
  GENRE_ROCK = 1;
  GENRE_INDIE = 2;
  GENRE_DRUM_AND_BASS = 3;
  // ...
}
```

Go 类型名与 proto 枚举名保持一致，不做修改：

```go
type Genre int32
```

该类型有一个 `String()` 方法，返回给定值对应的名称。

`Enum()` 方法会用给定值初始化新分配的内存，并返回相应的指针：

```go
func (Genre) Enum() *Genre
```

Protobuf 编译器会为枚举中的每个值生成一个常量。对于消息内部的枚举，常量名以外围消息的名称开头：

```go
const (
    Venue_KIND_UNSPECIFIED       Venue_Kind = 0
    Venue_KIND_CONCERT_HALL      Venue_Kind = 1
    Venue_KIND_STADIUM           Venue_Kind = 2
    Venue_KIND_BAR               Venue_Kind = 3
    Venue_KIND_OPEN_AIR_FESTIVAL Venue_Kind = 4
)
```

对于包级别的枚举，常量名则以枚举名开头：

```go
const (
    Genre_GENRE_UNSPECIFIED   Genre = 0
    Genre_GENRE_ROCK          Genre = 1
    Genre_GENRE_INDIE         Genre = 2
    Genre_GENRE_DRUM_AND_BASS Genre = 3
)
```

Protobuf 编译器还会生成两个映射（map）：一个从整数值映射到字符串名称，另一个从名称映射到整数值：

```go
var Genre_name = map[int32]string{
    0: "GENRE_UNSPECIFIED",
    1: "GENRE_ROCK",
    2: "GENRE_INDIE",
    3: "GENRE_DRUM_AND_BASS",
}
var Genre_value = map[string]int32{
    "GENRE_UNSPECIFIED":   0,
    "GENRE_ROCK":          1,
    "GENRE_INDIE":         2,
    "GENRE_DRUM_AND_BASS": 3,
}
```

请注意，`.proto` 语言允许多个枚举符号具有相同的数值。具有相同数值的符号互为同义词。它们在 Go 中的表示方式完全相同：多个名称对应同一个数值。反向映射中，每个数值只包含一个条目，对应 `.proto` 文件中最先出现的那个名称。

## 扩展（proto2） {#extensions}

给定一个扩展（extension）定义：

```proto
extend Concert {
  optional int32 promo_id = 123;
}
```

Protobuf 编译器会生成一个名为 `E_Promo_id` 的 [`protoreflect.ExtensionType`](https://pkg.go.dev/google.golang.org/protobuf/reflect/protoreflect?tab=doc#ExtensionType) 值。该值可以与 [`proto.GetExtension`](https://pkg.go.dev/google.golang.org/protobuf/proto?tab=doc#GetExtension)、[`proto.SetExtension`](https://pkg.go.dev/google.golang.org/protobuf/proto?tab=doc#SetExtension)、[`proto.HasExtension`](https://pkg.go.dev/google.golang.org/protobuf/proto?tab=doc#HasExtension) 和 [`proto.ClearExtension`](https://pkg.go.dev/google.golang.org/protobuf/proto?tab=doc#ClearExtension) 函数一起使用，以访问消息中的扩展。`GetExtension` 函数和 `SetExtension` 函数分别返回和接受一个包含扩展值类型的 `interface{}` 值。

对于单数标量扩展字段，扩展值类型是[标量值类型表](/programming-guides/proto3#scalar)中相应的 Go 类型。

对于单数内嵌消息扩展字段，扩展值类型是 `*M`，其中 `M` 是该字段的消息类型。

对于 repeated 扩展字段，扩展值类型是单数类型的切片。

例如，给定如下定义：

```proto
extend Concert {
  optional int32 singular_int32 = 1;
  repeated bytes repeated_strings = 2;
  optional Band singular_message = 3;
}
```

扩展值可以按如下方式访问：

```go
m := &somepb.Concert{}
proto.SetExtension(m, extpb.E_SingularInt32, int32(1))
proto.SetExtension(m, extpb.E_RepeatedString, []string{"a", "b", "c"})
proto.SetExtension(m, extpb.E_SingularMessage, &extpb.Band{})

v1 := proto.GetExtension(m, extpb.E_SingularInt32).(int32)
v2 := proto.GetExtension(m, extpb.E_RepeatedString).([][]byte)
v3 := proto.GetExtension(m, extpb.E_SingularMessage).(*extpb.Band)
```

扩展可以声明嵌套在另一个类型内部。例如，一种常见的模式如下：

```proto
message Promo {
  extend Concert {
    optional int32 promo_id = 124;
  }
}
```

在这种情况下，`ExtensionType` 值的名称为 `E_Promo_Concert`。

## 服务 {#service}

默认情况下，Go 代码生成器不会为服务（service）生成输出。如果你启用 [gRPC](https://www.grpc.io/) 插件（参见 [gRPC Go 快速开始指南](https://github.com/grpc/grpc-go/tree/master/examples)），则会生成支持 gRPC 的代码。

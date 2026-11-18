+++
title = "Go 生成代码指南（开放）"
weight = 610
linkTitle = "生成代码指南（开放）"
description = "详细描述 Protobuf 编译器针对任意给定协议定义所生成的 Go 代码。"
type = "docs"
source_url = "https://protobuf.dev/reference/go/go-generated/"
upstream_commit = "f72a6a648b34e9e098cbce1519bc9c8139105d66"
translated_at = "2026-11-19"
status = "translated"
translator = "agent"
+++

proto2、proto3 与版次（edition）生成代码之间的任何差异都会重点标出。请注意，这些差异存在于本文档所描述的生成代码（generated code）中，而非基础 API——后者在两个版本（version）中都是相同的。阅读本文档之前，请先阅读 [proto2 语言指南](/programming-guides/proto2)、[proto3 语言指南](/programming-guides/proto3)或 [版次语言指南](/programming-guides/editions)。

{{% alert title="Note" color="warning" %}}你正在查看的是旧生成代码 API（Open Struct API）的文档。如需（新）Opaque API 的对应文档，请参阅 [Go 生成代码（不透明）](/reference/go/go-generated-opaque)。Opaque API 的介绍请参见 [Go Protobuf: The new Opaque API](https://go.dev/blog/protobuf-opaque)。 {{% /alert %}}

## 编译器调用 {#invocation}

Protobuf 编译器需要一个插件（plugin）来生成 Go 代码。请使用 Go 1.16 或更高版本，运行以下命令进行安装：

```shell
go install google.golang.org/protobuf/cmd/protoc-gen-go@latest
```

这会将一个 `protoc-gen-go` 二进制文件安装到 `$GOBIN` 中。你可以设置 `$GOBIN` 环境变量来更改安装位置。它必须位于你的 `$PATH` 中，Protobuf 编译器才能找到它。

使用 `go_out` 标志调用时，Protobuf 编译器会生成 Go 输出。`go_out` 标志的参数是你希望编译器写入 Go 输出的目录。编译器会为每个输入的 `.proto` 文件创建一个源文件。输出文件的名称是通过将 `.proto` 扩展名替换为 `.pb.go` 得到的。

生成的 `.pb.go` 文件在输出目录中的具体存放位置取决于编译器标志。有以下几种输出模式：

-   如果指定了 `paths=import` 标志，输出文件会被放置在以 Go 包的导入路径命名的目录中（例如由 `.proto` 文件内的 `go_package` 选项指定的路径）。例如，输入文件 `protos/buzz.proto` 的 Go 导入路径为 `example.com/project/protos/fizz`，则输出文件位于 `example.com/project/protos/fizz/buzz.pb.go`。如果未指定 `paths` 标志，这就是默认的输出模式。
-   如果指定了 `module=$PREFIX` 标志，输出文件会被放置在以 Go 包的导入路径命名的目录中（例如由 `.proto` 文件内的 `go_package` 选项指定的路径），但会从输出文件名中移除指定的目录前缀。例如，输入文件 `protos/buzz.proto` 的 Go 导入路径为 `example.com/project/protos/fizz`，且 `example.com/project` 被指定为 `module` 前缀，则输出文件位于 `protos/fizz/buzz.pb.go`。在模块路径之外生成任何 Go 包都会导致错误。这种模式适合把生成的文件直接输出到 Go 模块中。
-   如果指定了 `paths=source_relative` 标志，输出文件会被放置在与输入文件相同的相对目录中。例如，输入文件 `protos/buzz.proto` 会生成位于 `protos/buzz.pb.go` 的输出文件。

`protoc-gen-go` 专属的标志通过在调用 `protoc` 时传入 `go_opt` 标志来提供。可以传入多个 `go_opt` 标志。例如，运行以下命令时：

```shell
protoc --proto_path=src --go_out=out --go_opt=paths=source_relative foo.proto bar/baz.proto
```

编译器会从 `src` 目录中读取输入文件 `foo.proto` 和 `bar/baz.proto`，并将输出文件 `foo.pb.go` 和 `bar/baz.pb.go` 写入 `out` 目录。必要时，编译器会自动创建嵌套的输出子目录，但不会创建输出目录本身。

## 包 {#package}

要生成 Go 代码，必须为每个 `.proto` 文件（包括被生成的 `.proto` 文件所间接依赖的文件）提供 Go 包的导入路径。指定 Go 导入路径有两种方式：

-   在 `.proto` 文件内声明，或
-   在调用 `protoc` 时于命令行上声明。

我们建议在 `.proto` 文件内声明，这样 `.proto` 文件对应的 Go 包就能随 `.proto` 文件本身集中标识，同时还能简化调用 `protoc` 时需要传递的标志集合。如果某个 `.proto` 文件的 Go 导入路径既在 `.proto` 文件本身中提供，又在命令行上提供，则以后者为准。

在 `.proto` 文件中，可以通过声明一个带有 Go 包完整导入路径的 `go_package` 选项来就地指定 Go 导入路径。用法示例：

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

由于所有 `.proto` 文件到其 Go 导入路径的映射可能相当庞大，这种指定 Go 导入路径的方式通常由掌控整个依赖树的构建工具（例如 [Bazel](https://bazel.build/)）来完成。如果同一个 `.proto` 文件存在重复条目，则以最后指定的为准。

对于 `go_package` 选项和 `M` 标志，其值都可以包含一个显式的包名，包名与导入路径之间以分号分隔。例如：“example.com/protos/foo;package_name”。不建议这种用法，因为默认情况下会以合理的方式从导入路径推导出包名。

导入路径用于确定当一个 `.proto` 文件导入另一个 `.proto` 文件时，必须生成哪些 import 语句。例如，如果 `a.proto` 导入了 `b.proto`，那么生成的 `a.pb.go` 文件就需要导入包含所生成 `b.pb.go` 文件的 Go 包（除非两个文件位于同一个包中）。导入路径还用于构造输出文件名。详情请参阅上文的“编译器调用”部分。

Go 导入路径与 `.proto` 文件中的 [`package` 指示符](/programming-guides/proto3#packages)之间没有任何关联。后者只与 Protobuf 命名空间（namespace）相关，而前者只与 Go 命名空间相关。此外，Go 导入路径与 `.proto` 导入路径之间也没有关联。

## API 级别 {#apilevel}

生成代码要么使用 Open Struct API，要么使用 Opaque API。介绍请参见博客文章 [Go Protobuf: The new Opaque API](https://go.dev/blog/protobuf-opaque)。

根据你的 `.proto` 文件所使用的语法，将使用的 API 如下：

`.proto` 语法 | API 级别
--------------- | ----------
proto2          | Open Struct API
proto3          | Open Struct API
版次 2023       | Open Struct API
版次 2024+      | Opaque API

你可以在 `.proto` 文件中设置 `api_level` 这个版次特性（feature）来选择 API。它可以按文件或按消息（message）设置：

```proto
edition = "2023";

package log;

import "google/protobuf/go_features.proto";
option features.(pb.go).api_level = API_OPAQUE;

message LogEntry { … }
```

为方便起见，你也可以用 `protoc` 命令行标志覆盖默认的 API 级别：

```
protoc […] --go_opt=default_api_level=API_HYBRID
```

要为特定文件（而非所有文件）覆盖默认 API 级别，请使用 `apilevelM` 映射标志（类似于[导入路径所用的 `M` 标志](/reference/go/go-generated/#package)）：

```
protoc […] --go_opt=apilevelMhello.proto=API_HYBRID
```

这些命令行标志对仍在使用 proto2 或 proto3 语法的 `.proto` 文件同样有效；但如果你想直接在 `.proto` 文件中选择 API 级别，则需要先把该文件迁移到版次（edition）。

## 消息 {#message}

给定一个简单的消息声明：

```proto
message Artist {}
```

Protobuf 编译器会生成一个名为 `Artist` 的结构体。`*Artist` 实现了 [`proto.Message`](https://pkg.go.dev/google.golang.org/protobuf/proto?tab=doc#Message) 接口。

[`proto` 包](https://pkg.go.dev/google.golang.org/protobuf/proto?tab=doc)提供了一组操作消息的函数，包括与二进制格式（binary format）之间的相互转换。

`proto.Message` 接口定义了一个 `ProtoReflect` 方法。该方法返回一个 [`protoreflect.Message`](https://pkg.go.dev/google.golang.org/protobuf/reflect/protoreflect?tab=doc#Message)，提供消息的基于反射（reflection）的视图。

`optimize_for` 选项不会影响 Go 代码生成器（code generator）的输出。

当多个 goroutine 并发访问同一个消息时，适用以下规则：

*   并发访问（读取）字段（field）是安全的，但有一个例外：
    *   首次访问[惰性字段（lazy field）](https://github.com/protocolbuffers/protobuf/blob/cacb096002994000f8ccc6d9b8e1b5b0783ee561/src/google/protobuf/descriptor.proto#L609)算作一次修改。
*   在同一个消息中修改不同的字段是安全的。
*   并发修改同一个字段是不安全的。
*   在调用 [`proto` 包](https://pkg.go.dev/google.golang.org/protobuf/proto?tab=doc)的函数（如 [`proto.Marshal`](https://pkg.go.dev/google.golang.org/protobuf/proto#Marshal) 或 [`proto.Size`](https://pkg.go.dev/google.golang.org/protobuf/proto#Size)）的同时，以任何方式并发修改消息都是不安全的。

### 嵌套类型

消息可以声明在另一个消息内部。例如：

```proto
message Artist {
  message Name {
  }
}
```

此时，编译器会生成两个结构体：`Artist` 和 `Artist_Name`。

## 字段

对于消息中定义的每个字段，Protobuf 编译器都会生成一个对应的结构体字段。该字段的具体形式取决于其类型，以及它是单数（singular）、repeated、map 还是 oneof 字段。

请注意，生成的 Go 字段名（field name）始终采用驼峰式（camel-case）命名，即使 `.proto` 文件中的字段名使用小写字母加下划线的形式（[也理应如此](/programming-guides/style#message-field-names)）。大小写转换规则如下：

1.  首字母大写以便导出。如果首字符是下划线，则移除该下划线，并在前面加上大写字母 X。
2.  如果内部的下划线后面跟着小写字母，则移除该下划线，并将后面的字母大写。

因此，proto 字段 `birth_year` 在 Go 中变为 `BirthYear`，而 `_birth_year_2` 变为 `XBirthYear_2`。

<a id="singular-scalar-proto2"></a>

### 单数显式存在性标量字段 {#singular-explicit}

对于如下字段定义：

```proto
int32 birth_year = 1;
```

编译器会生成一个结构体，其中包含名为 `BirthYear` 的 `*int32` 字段以及访问器（accessor）方法 `GetBirthYear()`；该方法返回 `Artist` 中的 `int32` 值，如果该字段未设置，则返回默认值（default value）。如果未显式设置默认值，则改用该类型的[零值（zero value）](https://golang.org/ref/spec#The_zero_value)（数字为 `0`，字符串为空字符串）。

对于其他标量（scalar）字段类型（包括 `bool`、`bytes` 和 `string`），`*int32` 会根据[标量值类型表](/programming-guides/proto2#scalar)替换为相应的 Go 类型。

<a id="singular-scalar-proto3"></a>

### 单数隐式存在性标量字段 {#singular-implicit}

对于如下字段定义：

```proto
int32 birth_year = 1;
```

编译器会生成一个结构体，其中包含名为 `BirthYear` 的 `int32` 字段以及访问器方法 `GetBirthYear()`；该方法返回 `birth_year` 中的 `int32` 值，如果该字段未设置，则返回该类型的[零值](https://golang.org/ref/spec#The_zero_value)（数字为 `0`，字符串为空字符串）。

`FirstActiveYear` 结构体字段的类型将是 `*int32`，因为它被标记为 `optional`。

对于其他标量字段类型（包括 `bool`、`bytes` 和 `string`），`int32` 会根据[标量值类型表](/programming-guides/proto3#scalar)替换为相应的 Go 类型。proto 中未设置的值将表示为该类型的[零值](https://golang.org/ref/spec#The_zero_value)（数字为 `0`，字符串为空字符串）。

### 单数消息字段 {#singular-message}

给定如下消息类型：

```proto
message Band {}
```

对于含有 `Band` 字段的消息：

```proto
// proto2
message Concert {
  optional Band headliner = 1;
  // 如果使用 required 而不是 optional，生成的代码结果相同。
}

// proto3
message Concert {
  Band headliner = 1;
}

// 版次
message Concer {
  Band headliner = 1;
}
```

编译器会生成如下 Go 结构体：

```go
type Concert struct {
    Headliner *Band
}
```

消息字段可以设置为 `nil`，这表示该字段未设置，实际上相当于清除了该字段。这与将值设置为消息结构体的\"空\"实例并不等价。

编译器还会生成辅助函数 `func (m *Concert) GetHeadliner() *Band`。如果 `m` 为 nil 或 `headliner` 未设置，该函数会返回 `nil` 的 `*Band`。这使得无需中间 `nil` 检查即可进行链式 get 调用：

```go
var m *Concert // 默认为 nil
log.Infof("GetFoundingYear() = %d (no panic!)", m.GetHeadliner().GetFoundingYear())
```

### repeated 字段 {#repeated}

每个 repeated 字段都会在 Go 结构体中生成一个 `T` 类型的切片字段，其中 `T` 是该字段的元素类型。对于如下含有 repeated 字段的消息：

```proto
message Concert {
  // 最佳实践：repeated 字段使用复数名称：
  // /programming-guides/style#repeated-fields
  repeated Band support_acts = 1;
}
```

编译器会生成如下 Go 结构体：

```go
type Concert struct {
    SupportActs []*Band
}
```

同样，对于字段定义 `repeated bytes band_promo_images = 1;`，编译器会生成一个含有名为 `BandPromoImage` 的 `[][]byte` 字段的 Go 结构体。对于 repeated [枚举](#enum)（如 `repeated MusicGenre genres = 2;`），编译器会生成一个含有名为 `Genre` 的 `[]MusicGenre` 字段的结构体。

下面的示例展示了如何设置该字段：

```go
concert := &Concert{
  SupportActs: []*Band{
    {}, // 第一个元素。
    {}, // 第二个元素。
  },
}
```

要访问该字段，可以这样做：

```go
support := concert.GetSupportActs() // support 的类型是 []*Band。
b1 := support[0] // b1 的类型是 *Band，即 support_acts 中的第一个元素。
```

### map 字段 {#map}

每个 map 字段都会在结构体中生成一个 `map[TKey]TValue` 类型的字段，其中 `TKey` 是字段的键（key）类型，`TValue` 是字段的值（value）类型。对于如下含有 map 字段的消息：

```proto
message MerchItem {}

message MerchBooth {
  // items 将商品项名称（"Signed T-Shirt"）映射到
  // 包含该商品更多详情的 MerchItem 消息。
  map<string, MerchItem> items = 1;
}
```

编译器会生成如下 Go 结构体：

```go
type MerchBooth struct {
    Items map[string]*MerchItem
}
```

### oneof 字段 {#oneof}

对于 oneof 字段，Protobuf 编译器会生成一个接口类型为 `isMessageName_MyField` 的单一字段。它还会为 oneof 中的每个[单数字段](#singular-scalar-proto2)生成一个结构体，这些结构体均实现了该 `isMessageName_MyField` 接口。

对于如下含有 oneof 字段的消息：

```proto
package account;
message Profile {
  oneof avatar {
    string image_url = 1;
    bytes image_data = 2;
  }
}
```

编译器会生成如下结构体：

```go
type Profile struct {
    // 可赋给 Avatar 的类型：
    //  *Profile_ImageUrl
    //  *Profile_ImageData
    Avatar isProfile_Avatar `protobuf_oneof:"avatar"`
}

type Profile_ImageUrl struct {
        ImageUrl string
}
type Profile_ImageData struct {
        ImageData []byte
}
```

`*Profile_ImageUrl` 和 `*Profile_ImageData` 都通过提供空的 `isProfile_Avatar()` 方法来实现 `isProfile_Avatar`。

下面的示例展示了如何设置该字段：

```go
p1 := &account.Profile{
  Avatar: &account.Profile_ImageUrl{ImageUrl: "http://example.com/image.png"},
}

// imageData 是 []byte
imageData := getImageData()
p2 := &account.Profile{
  Avatar: &account.Profile_ImageData{ImageData: imageData},
}
```

要访问该字段，可以对值使用类型 switch 来处理不同的消息类型。

```go
switch x := m.Avatar.(type) {
case *account.Profile_ImageUrl:
    // 基于 URL 加载个人资料图片
    // 使用 x.ImageUrl
case *account.Profile_ImageData:
    // 基于字节加载个人资料图片
    // 使用 x.ImageData
case nil:
    // 该字段未设置。
default:
    return fmt.Errorf("Profile.Avatar has unexpected type %T", x)
}
```

编译器还会生成 get 方法 `func (m *Profile) GetImageUrl() string` 和 `func (m *Profile) GetImageData() []byte`。每个 get 函数都会返回该字段的值；如果字段未设置，则返回零值。

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

Protobuf 编译器会生成一个类型，以及一系列该类型的常量：

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

对于消息内的枚举（如上例），类型名以消息名开头：

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

Go 类型名与 proto 枚举名保持一致：

```go
type Genre int32
```

该类型有一个 `String()` 方法，用于返回给定值的名称。

`Enum()` 方法会以给定值初始化新分配的内存，并返回相应的指针：

```go
func (Genre) Enum() *Genre
```

Protobuf 编译器会为枚举中的每个值生成一个常量。对于消息内的枚举，常量以外围消息的名称开头：

```go
const (
    Venue_KIND_UNSPECIFIED       Venue_Kind = 0
    Venue_KIND_CONCERT_HALL      Venue_Kind = 1
    Venue_KIND_STADIUM           Venue_Kind = 2
    Venue_KIND_BAR               Venue_Kind = 3
    Venue_KIND_OPEN_AIR_FESTIVAL Venue_Kind = 4
)
```

而对于包级别的枚举，常量则以枚举名开头：

```go
const (
    Genre_GENRE_UNSPECIFIED   Genre = 0
    Genre_GENRE_ROCK          Genre = 1
    Genre_GENRE_INDIE         Genre = 2
    Genre_GENRE_DRUM_AND_BASS Genre = 3
)
```

Protobuf 编译器还会生成一个从整数值到字符串名称的映射，以及一个从名称到值的映射：

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

请注意，`.proto` 语言允许多个枚举符号具有相同的数值。具有相同数值的符号互为同义词。它们在 Go 中的表示方式完全相同：多个名称对应同一个数值。反向映射中每个数值只包含一个条目，对应 .proto 文件中最先出现的那个名称。

## 扩展 {#extensions}

给定一个扩展（extension）定义：

```proto
extend Concert {
  int32 promo_id = 123;
}
```

Protobuf 编译器会生成一个名为 `E_Promo_id` 的 [`protoreflect.ExtensionType`](https://pkg.go.dev/google.golang.org/protobuf/reflect/protoreflect?tab=doc#ExtensionType) 值。该值可与 [`proto.GetExtension`](https://pkg.go.dev/google.golang.org/protobuf/proto?tab=doc#GetExtension)、[`proto.SetExtension`](https://pkg.go.dev/google.golang.org/protobuf/proto?tab=doc#SetExtension)、[`proto.HasExtension`](https://pkg.go.dev/google.golang.org/protobuf/proto?tab=doc#HasExtension) 和 [`proto.ClearExtension`](https://pkg.go.dev/google.golang.org/protobuf/proto?tab=doc#ClearExtension) 函数一起使用，以访问消息中的扩展。`GetExtension` 函数与 `SetExtension` 函数分别返回和接受一个包含扩展值类型的 `interface{}` 值。

对于单数标量扩展字段，扩展值类型是[标量值类型表](/programming-guides/proto3#scalar)中对应的 Go 类型。

对于单数内嵌消息扩展字段，扩展值类型是 `*M`，其中 `M` 是该字段的消息类型。

对于 repeated 扩展字段，扩展值类型是单数类型的切片。

例如，给定如下定义：

```proto
extend Concert {
  int32 singular_int32 = 1;
  repeated bytes repeated_strings = 2;
  Band singular_message = 3;
}
```

扩展值的访问方式如下：

```go
m := &somepb.Concert{}
proto.SetExtension(m, extpb.E_SingularInt32, int32(1))
proto.SetExtension(m, extpb.E_RepeatedString, []string{"a", "b", "c"})
proto.SetExtension(m, extpb.E_SingularMessage, &extpb.Band{})

v1 := proto.GetExtension(m, extpb.E_SingularInt32).(int32)
v2 := proto.GetExtension(m, extpb.E_RepeatedString).([][]byte)
v3 := proto.GetExtension(m, extpb.E_SingularMessage).(*extpb.Band)
```

扩展可以声明在另一个类型的内部。例如，一种常见的模式是像这样写：

```proto
message Promo {
  extend Concert {
    int32 promo_id = 124;
  }
}
```

此时，`ExtensionType` 值的名称为 `E_Promo_Concert`。

## 服务 {#service}

默认情况下，Go 代码生成器不会为服务（service）生成任何输出。如果启用 [gRPC](https://www.grpc.io/) 插件（参见 [gRPC Go 快速开始指南](https://github.com/grpc/grpc-go/tree/master/examples)），则会生成用于支持 gRPC 的代码。

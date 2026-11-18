+++
title = "Go 常见问题"
weight = 620
linkTitle = "常见问题"
description = "关于在 Go 中实现 Protobuf 的常见问题列表，每个问题均附有答案。"
type = "docs"
source_url = "https://protobuf.dev/reference/go/faq/"
upstream_commit = "f72a6a648b34e9e098cbce1519bc9c8139105d66"
translated_at = "2026-11-19"
status = "translated"
translator = "agent"
+++

## 版本

### `github.com/golang/protobuf` 与 `google.golang.org/protobuf` 有什么区别？ {#modules}

[`github.com/golang/protobuf`](https://pkg.go.dev/github.com/golang/protobuf?tab=overview) 模块是最初的 Go Protobuf API。

[`google.golang.org/protobuf`](https://pkg.go.dev/google.golang.org/protobuf?tab=overview) 模块是该 API 的升级版本，其设计目标是简洁、易用和安全。升级版 API 的旗舰特性（feature）包括对反射（reflection）的支持，以及面向用户的 API 与底层实现的分离。

我们建议你在新代码中使用 `google.golang.org/protobuf`。

`github.com/golang/protobuf` 的 `v1.4.0` 及更高版本封装了新实现，让程序能够逐步采用新 API。例如，`github.com/golang/protobuf/ptypes` 中定义的知名类型（well-known types）只是较新模块中所定义类型的别名。因此，[`google.golang.org/protobuf/types/known/emptypb`](https://pkg.go.dev/google.golang.org/protobuf/types/known/emptypb) 与 [`github.com/golang/protobuf/ptypes/empty`](https://pkg.go.dev/github.com/golang/protobuf/ptypes/empty) 可以互换使用。

### `proto1`、`proto2`、`proto3` 和版次（editions）是什么？ {#proto-versions}

这些是 Protobuf *语言*的不同修订版本。它们与 Protobuf 的 Go *实现*是两回事。

*   **版次（Editions）**是编写 Protobuf 模式（schema）的最新方式，也是推荐的方式。新特性将随新版次一同发布。更多信息请参阅 [Protobuf 版次](/editions)。

*   `proto3` 是这门语言的旧版本。我们鼓励新代码使用版次。

*   `proto2` 是这门语言的旧版本。尽管已被 proto3 和版次取代，proto2 仍然受到完整支持。

*   `proto1` 是这门语言的已废弃版本。它从未以开源形式发布过。

### 有几种不同的 `Message` 类型，应该使用哪一种？ {#message-types}

*   [`"google.golang.org/protobuf/proto".Message`](https://pkg.go.dev/google.golang.org/protobuf/proto?tab=doc#Message) 是一个接口类型，由当前版本的 Protobuf 编译器生成的所有消息（message）实现。操作任意消息的函数（例如 [`proto.Marshal`](https://pkg.go.dev/google.golang.org/protobuf/proto?tab=doc#Marshal) 或 [`proto.Clone`](https://pkg.go.dev/google.golang.org/protobuf/proto?tab=doc#Clone)）接受或返回此类型。

*   [`"google.golang.org/protobuf/reflect/protoreflect".Message`](https://pkg.go.dev/google.golang.org/protobuf/reflect/protoreflect?tab=doc#Message) 是一个描述消息反射视图的接口类型。

    在 `proto.Message` 上调用 `ProtoReflect` 方法即可得到 `protoreflect.Message`。

*   [`"google.golang.org/protobuf/reflect/protoreflect".ProtoMessage`](https://pkg.go.dev/google.golang.org/protobuf/reflect/protoreflect?tab=doc#ProtoMessage) 是 `"google.golang.org/protobuf/proto".Message` 的别名。这两种类型可以互换使用。

*   [`"github.com/golang/protobuf/proto".Message`](https://pkg.go.dev/github.com/golang/protobuf/proto?tab=doc#Message) 是由旧版 Go Protobuf API 定义的接口类型。所有生成的消息类型都实现了该接口，但该接口并未描述这些消息应有的行为。新代码应避免使用此类型。

## 常见问题

### "`go install`"：`working directory is not part of a module` {#working-directory}

在 Go 1.15 及更低版本上，你设置了环境变量 `GO111MODULE=on`，并在模块目录之外运行 `go install` 命令。请将 `GO111MODULE` 设置为 `auto`，或者取消设置该环境变量。

在 Go 1.16 及更高版本上，通过指定明确的版本，`go install` 可以在模块之外调用：`go install google.golang.org/protobuf/cmd/protoc-gen-go@latest`

### `constant -1 overflows protoimpl.EnforceVersion` {#enforce-version}

你正在使用一个生成的 `.pb.go` 文件，该文件需要较新版本的 `"google.golang.org/protobuf"` 模块。

使用以下命令更新到较新版本：

```shell
go get -u google.golang.org/protobuf/proto
```

### `undefined: "github.com/golang/protobuf/proto".ProtoPackageIsVersion4` {#enforce-version-apiv1}

你正在使用一个生成的 `.pb.go` 文件，该文件需要较新版本的 `"github.com/golang/protobuf"` 模块。

使用以下命令更新到较新版本：

```shell
go get -u github.com/golang/protobuf/proto
```

### 什么是 Protobuf 命名空间冲突？ {#namespace-conflict}

所有链接进 Go 二进制文件的 Protobuf 声明都会被插入一个全局注册表（registry）中。

每个 Protobuf 声明（例如枚举（enum）、枚举值或消息）都有一个绝对名称，它由[包名（package name）](/programming-guides/proto2#packages)与该声明在 `.proto` 源文件中的相对名称拼接而成（例如 `my.proto.package.MyMessage.NestedMessage`）。Protobuf 语言假定所有声明在全局范围内都是唯一的。

如果链接进同一个 Go 二进制文件的两个 Protobuf 声明具有相同的名称，就会导致命名空间（namespace）冲突，注册表将无法按名称正确解析该声明。根据所使用的 Go Protobuf 版本不同，这种情况要么会在初始化时 panic，要么会静默丢弃冲突，并在稍后的运行时（runtime）引发潜在缺陷。

### 如何修复 Protobuf 命名空间冲突？ {#fix-namespace-conflict}

修复命名空间冲突的最佳方式取决于冲突产生的原因。

命名空间冲突的常见成因：

*   **被 vendored 的 .proto 文件。**当同一个 `.proto` 文件被生成到两个或更多 Go 包中并链接进同一个 Go 二进制文件时，它会在生成的 Go 包内的每个 Protobuf 声明上发生冲突。这种情况通常发生在某个 `.proto` 文件被 vendored 并从中生成 Go 包时，或者生成的 Go 包本身被 vendored 时。用户应当避免 vendoring，转而依赖为该 `.proto` 文件提供的一个集中式 Go 包。

    *   如果某个 `.proto` 文件由外部方持有且缺少 `go_package` 选项（option），那么你应当与该 `.proto` 文件的持有者协调，指定一个可供众多用户共同依赖的集中式 Go 包。

*   **缺失或过于通用的 proto 包名。**如果某个 `.proto` 文件没有指定包名，或者使用了过于通用的包名（例如 "my_service"），那么该文件中的声明就很有可能与其他任何地方的声明发生冲突。我们建议每个 `.proto` 文件都使用一个经过深思熟虑、在全局范围内唯一的包名（例如以公司名称作为前缀）。

{{% alert title="Warning" color="warning" %}}
追溯性地更改 `.proto` 文件的包名，对于用作扩展字段（extension field）的类型、存储在 `google.protobuf.Any` 中的类型，以及 gRPC 服务（service）定义而言，都不是向后兼容（backwards compatible）的。{{% /alert %}}

从 `google.golang.org/protobuf` 模块的 v1.26.0 版本开始，如果链接进 Go 程序的 Protobuf 名称中存在多个相互冲突的名称，程序启动时将报告硬性错误。虽然最好修复冲突的根源，但这个致命错误可以立即通过以下两种方式之一绕过：

1.  **在编译时。**处理冲突的默认行为可以在编译时通过一个由链接器初始化的变量来指定：`go build -ldflags "-X google.golang.org/protobuf/reflect/protoregistry.conflictPolicy=warn"`

2.  **在程序执行时。**执行某个特定 Go 二进制文件时处理冲突的行为可以通过环境变量来设置：`GOLANG_PROTOBUF_REGISTRATION_CONFLICT=warn ./main`

### 如何使用 Protobuf 版次？ {#using-editions}

要使用某个 Protobuf 版次（edition），你必须在 `.proto` 文件中指定该版次。例如，要使用 2023 版次，请在 `.proto` 文件顶部添加以下内容：

```proto
edition = "2023";
```

随后，Protobuf 编译器会生成与指定版次兼容的 Go 代码。通过版次，你还可以为 `.proto` 文件启用或禁用特定特性。更多信息请参阅 [Protobuf 版次](/editions/overview)。

### 如何控制生成的 Go 代码的行为？ {#controlling-generated-code}

通过版次，你可以在 `.proto` 文件中启用或禁用特定特性，从而控制所生成的 Go 代码（generated code）的行为。例如，要为你的实现设置 API 行为，请在 `.proto` 文件中添加以下内容：

```proto
edition = "2023";

option features.(pb.go).api_level = API_OPAQUE;
```

当 `api_level` 设置为 `API_OPAQUE` 时，Protobuf 编译器生成的 Go 代码会隐藏结构体字段，使其无法再被直接访问。取而代之的是，会创建新的访问器（accessor）方法来读取、设置或清除字段。

有关可用特性及其说明的完整列表，请参阅[版次特性](/editions/features)。

### 为什么 `reflect.DeepEqual` 处理 Protobuf 消息时的表现不符合预期？ {#deepequal}

生成的 Protobuf 消息类型包含内部状态，即使是相互等价的消息，其内部状态也可能不同。

此外，`reflect.DeepEqual` 函数并不理解 Protobuf 消息的语义，可能会报告实际并不存在的差异。例如，包含 `nil` map 的 map 字段与包含长度为零、非 `nil` map 的 map 字段在语义上是等价的，但 `reflect.DeepEqual` 会将它们报告为不相等。

请使用 [`proto.Equal`](https://pkg.go.dev/google.golang.org/protobuf/proto#Equal) 函数来比较消息值。

在测试中，你还可以将 [`"github.com/google/go-cmp/cmp"`](https://pkg.go.dev/github.com/google/go-cmp/cmp?tab=doc) 包与 [`protocmp.Transform()`](https://pkg.go.dev/google.golang.org/protobuf/testing/protocmp#Transform) 选项结合使用。`cmp` 包可以比较任意数据结构，[`cmp.Diff`](https://pkg.go.dev/github.com/google/go-cmp/cmp#Diff) 会生成人类可读的值差异报告。

```go
if diff := cmp.Diff(a, b, protocmp.Transform()); diff != "" {
  t.Errorf("unexpected difference:\n%v", diff)
}
```

## Hyrum 定律

### 什么是 Hyrum 定律？为什么它会出现在本常见问题列表中？ {#hyrums-law}

[Hyrum 定律](https://www.hyrumslaw.com/)的内容是：

> 当一个 API 的用户数量足够多时，无论你在契约中承诺什么都无关紧要：你的系统的所有可观察行为都会被某个人所依赖。

最新版 Go Protobuf API 的一个设计目标是：尽可能避免提供那些我们无法承诺未来保持稳定的可观察行为。我们的理念是：在我们未作任何承诺的领域中刻意保持不稳定，要好于制造稳定的假象——等到假象在将来被打破时，项目可能早已长期依赖这一错误假设了。

### 为什么错误信息的文本一直在变化？ {#unstable-errors}

依赖错误信息确切文本的测试很脆弱，一旦文本发生变化就容易失效。为了劝阻在测试中以不安全的方式使用错误文本，本模块产生的错误文本被刻意设计为不稳定的。

如果你需要判断某个错误是否由 [`protobuf`](https://pkg.go.dev/mod/google.golang.org/protobuf) 模块产生，我们保证所有错误都会按照 [`errors.Is`](https://pkg.go.dev/errors?tab=doc#Is) 的判定与 [`proto.Error`](https://pkg.go.dev/google.golang.org/protobuf/proto?tab=doc#Error) 相匹配。

### 为什么 [`protojson`](https://pkg.go.dev/google.golang.org/protobuf/encoding/protojson) 的输出一直在变化？ {#unstable-json}

对于 Protobuf 的 [JSON 格式](/programming-guides/proto3#json)的 Go 实现，我们不对其长期稳定性作任何承诺。该规范只规定了什么是合法的 JSON，却没有规定一种*规范化*（canonical）格式，来约定序列化器（marshaler）应当*如何精确地*格式化给定的消息。为了避免制造输出稳定的假象，我们刻意引入了细微差异，使逐字节的比较很可能失败。

要获得一定程度的输出稳定性，我们建议将输出通过某个 JSON 格式化器处理。

### 为什么 [`prototext`](https://pkg.go.dev/google.golang.org/protobuf/encoding/prototext) 的输出一直在变化？ {#unstable-text}

对于文本格式（text format）的 Go 实现，我们不对其长期稳定性作任何承诺。Protobuf 文本格式目前尚无规范化（canonical）的规范说明，我们也希望保留未来改进 `prototext` 包输出的能力。既然我们不承诺该包输出的稳定性，便刻意引入了不稳定性，以劝阻用户依赖它。

要获得一定程度的稳定性，我们建议将 `prototext` 的输出交给 [`txtpbfmt`](https://github.com/protocolbuffers/txtpbfmt) 程序处理。该格式化器可以通过 [`parser.Format`](https://pkg.go.dev/github.com/protocolbuffers/txtpbfmt/parser?tab=doc#Format) 在 Go 中直接调用。

## 其他

### 如何将 Protobuf 消息用作哈希键？ {#hash}

你需要的是规范化序列化（canonical serialization），即 Protobuf 消息经过序列化后的输出能够保证随时间保持稳定。遗憾的是，目前尚不存在规范化序列化的规范。你需要自己编写一个，或者设法避免这种需求。

### 我可以向 Go Protobuf 实现添加新特性吗？ {#new-feature}

也许可以。我们向来乐于听取建议，但对添加新东西非常谨慎。

Protobuf 的 Go 实现力求与其他语言的实现保持一致。因此，我们倾向于回避那些过度专属于 Go 的特性。Go 特有的特性会妨碍 Protobuf 实现其作为语言无关（language-neutral）数据交换格式的目标。

如果你的想法并非专门针对 Go 实现，你应该加入 [Protobuf 讨论组](http://groups.google.com/group/protobuf)并在那里提出建议。

如果你有针对 Go 实现的想法，请在我们的问题追踪器（issue tracker）上提交 issue：
[https://github.com/golang/protobuf/issues](https://github.com/golang/protobuf/issues)

### 我可以为 `Marshal` 或 `Unmarshal` 添加选项来自定义它们吗？ {#new-marshal-option}

仅当该选项在其他实现（例如 C++、Java）中也存在时才可以。Protobuf 消息的编码（encoding）——二进制、JSON 和文本——在各实现之间必须保持一致，这样用一种语言编写的程序才能读取用另一种语言编写的消息。

除非至少有一个其他受支持的实现中存在等价的选项，否则我们不会向 Go 实现添加任何影响 `Marshal` 函数所输出数据或 `Unmarshal` 函数所读取数据的选项。

### 我可以自定义 `protoc-gen-go` 生成的代码吗？ {#custom-code}

总体而言，不可以。Protobuf 的定位是一种语言无关的数据交换格式，而针对特定实现的定制化与这一意图背道而驰。

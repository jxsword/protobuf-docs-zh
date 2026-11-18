+++
title = "Protobuf 基础：Go"
weight = 240
linkTitle = "Go"
description = "面向 Go 程序员的 Protobuf 使用基础入门。"
type = "docs"
source_url = "https://protobuf.dev/getting-started/gotutorial/"
upstream_commit = "f72a6a648b34e9e098cbce1519bc9c8139105d66"
translated_at = "2026-11-19"
status = "translated"
translator = "agent"
+++

本教程为 Go 程序员提供使用 Protobuf 的基础入门，使用的是 Protobuf 语言的 [proto3](/programming-guides/proto3) 版本。通过逐步创建一个简单的示例应用，它将向你展示如何：

-   在 `.proto` 文件中定义消息（message）格式。
-   使用 Protobuf 编译器。
-   使用 Go Protobuf API 写入和读取消息。

本文并不是一份在 Go 中使用 Protobuf 的全面指南。如需更详细的参考信息，请参阅 [Protobuf 语言指南](/programming-guides/proto3)、[Go API 参考](https://pkg.go.dev/google.golang.org/protobuf/proto)、[Go 生成代码指南](/reference/go/go-generated)以及[编码参考](/programming-guides/encoding)。

## 问题域 {#problem-domain}

我们要使用的示例是一个非常简单的“通讯录”应用，它可以把人们的联系信息写入文件，也可以从文件中读出。通讯录中的每个人都有姓名、ID、电子邮件地址和联系电话。

如何对这样的结构化数据（structured data）进行序列化（serialization）并读取出来？有以下几种解决办法：

-   使用 [gobs](//golang.org/pkg/encoding/gob/) 来序列化 Go 数据结构。在纯 Go 环境中，这是一个不错的方案，但如果你需要与为其他平台编写的应用共享数据，它的效果就不理想了。
-   你可以自行发明一种临时方式，把各数据项编码进单个字符串——例如把 4 个整数编码成 “12:3:-23:67”。这种方式简单而灵活，但需要专门编写一次性的编码与解析（parse）代码，而且解析会带来少量运行时开销。它最适合用于编码非常简单的数据。
-   将数据序列化为 XML。这种方式颇具吸引力，因为 XML（勉强）算是人类可读的，而且许多语言都有绑定库。如果你希望与其他应用/项目共享数据，这可能是个不错的选择。然而，XML 以极度占用空间而著称，对其进行编码/解码可能给应用带来巨大的性能损失。此外，遍历 XML DOM 树通常也比访问类中的简单字段（field）复杂得多。

Protobuf 正是为解决这一问题而生的灵活、高效、自动化方案。使用 Protobuf 时，你要为想要存储的数据结构编写一份 `.proto` 描述。Protobuf 编译器会据此创建一个类，以高效的二进制格式（binary format）实现 Protobuf 数据的自动编码与解析。生成的类为构成 Protobuf 消息的字段提供 getter 和 setter，并负责把消息作为一个整体进行读写时的各项细节。重要的是，Protobuf 格式支持随时间推移扩展格式，同时代码仍能读取以旧格式编码的数据。

## 在哪里找到示例代码 {#example-code}

我们的示例是一组命令行应用，用于管理以 Protobuf 编码的通讯录数据文件。命令 `add_person_go` 向数据文件添加一个新条目，命令 `list_people_go` 解析数据文件并把数据打印到控制台。

你可以在 GitHub 仓库的 [examples 目录](https://github.com/protocolbuffers/protobuf/tree/master/examples)中找到完整示例。

## 定义你的协议格式 {#protocol-format}

要创建你的通讯录应用，需要先从一个 `.proto` 文件开始。`.proto` 文件中的定义很简单：为每个想要序列化的数据结构添加一个*消息*，然后为消息中的每个字段指定名称和类型。在我们的示例中，定义这些消息的 `.proto` 文件是 [`addressbook.proto`](https://github.com/protocolbuffers/protobuf/blob/master/examples/addressbook.proto)。

`.proto` 文件以一条 package 声明开头，它有助于避免不同项目之间的命名冲突。

```proto
syntax = "proto3";
package tutorial;

import "google/protobuf/timestamp.proto";
```

`go_package` 选项定义了将包含此文件全部生成代码的包的导入路径。Go 包名就是该导入路径的最后一个路径组件。例如，我们的示例将使用包名 “tutorialpb”。

```proto
option go_package = "github.com/protocolbuffers/protobuf/examples/go/tutorialpb";
```

接下来是你的消息定义。消息只是一个包含一组带类型字段的聚合体（aggregate）。许多标准简单数据类型都可用作字段类型，包括 `bool`、`int32`、`float`、`double` 和 `string`。你还可以把其他消息类型用作字段类型，为消息添加更深层的结构。

```proto
message Person {
  string name = 1;
  int32 id = 2;  // 此人的唯一 ID 编号。
  string email = 3;

  message PhoneNumber {
    string number = 1;
    PhoneType type = 2;
  }

  repeated PhoneNumber phones = 4;

  google.protobuf.Timestamp last_updated = 5;
}

enum PhoneType {
  PHONE_TYPE_UNSPECIFIED = 0;
  PHONE_TYPE_MOBILE = 1;
  PHONE_TYPE_HOME = 2;
  PHONE_TYPE_WORK = 3;
}

// 我们的通讯录文件只是其中一条这样的消息。
message AddressBook {
  repeated Person people = 1;
}
```

在上面的示例中，`Person` 消息包含 `PhoneNumber` 消息，而 `AddressBook` 消息包含 `Person` 消息。你甚至可以把消息类型嵌套定义在其他消息内部——如你所见，`PhoneNumber` 类型就定义在 `Person` 之中。如果希望某个字段的取值限定在一组预定义值之内，你还可以定义枚举（`enum`）类型——这里的目的是指定电话号码可以是 `PHONE_TYPE_MOBILE`、`PHONE_TYPE_HOME` 或 `PHONE_TYPE_WORK` 之一。

每个元素上的 “ = 1”、“ = 2” 标记，标识出该字段在二进制编码中使用的唯一“标签”（tag）。字段编号 1-15 比更大的编号少用一个字节来编码，因此作为一种优化，你可以决定把这些标签用于常用或可重复（repeated）的元素，而把编号 16 及以上的标签留给不那么常用的 optional 元素。repeated 字段中的每个元素都需要重新编码字段编号，因此 repeated 字段尤其适合进行这种优化。

如果字段值未设置，就会使用[默认值](/programming-guides/proto3#default)：数值类型为 0，字符串为空字符串，布尔类型为 false。对于内嵌消息，默认值始终是该消息的“默认实例”（default instance）或“原型”（prototype）——一个所有字段均未设置的实例。调用访问器（accessor）获取一个未被显式设置的字段的值时，返回的总是该字段的默认值。

如果某个字段是 `repeated` 的，那么该字段可以重复任意多次（包括零次）。重复值的顺序会在 Protobuf 消息中得到保留。可以把 repeated 字段看作大小动态可变的数组。

关于编写 `.proto` 文件的完整指南——包括所有可能的字段类型——请参阅 [Protobuf 语言指南](/programming-guides/proto3)。不过，不要去找类似类继承的机制——Protobuf 并不支持这种做法。

## 编译你的 Protobuf 模式（schema）{#compiling-protocol-buffers}

现在你已经有 `.proto` 文件了，接下来要做的就是生成读写 `AddressBook`（因而也包括 `Person` 和 `PhoneNumber`）消息所需的类。为此，你需要对 `.proto` 运行 Protobuf 编译器 `protoc`：

1.  如果尚未安装编译器，请[下载软件包](/downloads)并按照 README 中的说明操作。

2.  运行以下命令，安装 Go Protobuf 插件（plugin）：

    ```shell
    go install google.golang.org/protobuf/cmd/protoc-gen-go@latest
    ```

    编译器插件 `protoc-gen-go` 将被安装到 `$GOBIN` 中，默认为 `$GOPATH/bin`。它必须位于你的 `$PATH` 中，协议编译器 `protoc` 才能找到它。

3.  现在运行编译器，指定源目录（你的应用源码所在的位置——如果未提供该值，则使用当前目录）、目标目录（希望生成的代码存放的位置；通常与 `$SRC_DIR` 相同），以及你的 `.proto` 的路径。在本例中，应执行以下命令：

    ```shell
    protoc -I=$SRC_DIR --go_out=$DST_DIR $SRC_DIR/addressbook.proto
    ```

    由于你想要的是 Go 代码，因此要使用 `--go_out` 选项——其他受支持的语言也提供了类似的选项。

这会在你指定的目标目录中生成 `github.com/protocolbuffers/protobuf/examples/go/tutorialpb/addressbook.pb.go`。

## Protobuf API {#protobuf-api}

生成 `addressbook.pb.go` 会为你提供以下有用的类型：

-   一个带有 `People` 字段的 `AddressBook` 结构体。
-   一个带有 `Name`、`Id`、`Email` 和 `Phones` 字段的 `Person` 结构体。
-   一个带有 `Number` 和 `Type` 字段的 `Person_PhoneNumber` 结构体。
-   `Person_PhoneType` 类型，以及为 `Person.PhoneType` 枚举中的每个取值定义的对应值。

关于究竟生成了哪些内容的细节，你可以在 [Go 生成代码指南](/reference/go/go-generated)中进一步了解；不过在大多数情况下，你完全可以把这些类型当作普通的 Go 类型来对待。

下面这个例子来自 [`list_people` 命令的单元测试](https://github.com/protocolbuffers/protobuf/blob/master/examples/go/cmd/list_people/list_people_test.go)，展示了你可以如何创建一个 `Person` 实例：

```go
p := pb.Person{
    Id:    1234,
    Name:  "John Doe",
    Email: "jdoe@example.com",
    Phones: []*pb.Person_PhoneNumber{
        {Number: "555-4321", Type: pb.PhoneType_PHONE_TYPE_HOME},
    },
}
```

## 写入消息 {#writing-a-message}

使用 Protobuf 的全部意义就在于把你的数据序列化，以便在其他地方进行解析。在 Go 中，你使用 `proto` 库的 [Marshal](https://pkg.go.dev/google.golang.org/protobuf/proto?tab=doc#Marshal) 函数来序列化你的 Protobuf 数据。指向 Protobuf 消息 `struct` 的指针实现了 `proto.Message` 接口。调用 `proto.Marshal` 会返回以线路格式（wire format）编码的 Protobuf 消息。例如，我们在 [`add_person` 命令](https://github.com/protocolbuffers/protobuf/blob/master/examples/go/cmd/add_person/add_person.go)中就使用了这个函数：

```go
book := &pb.AddressBook{}
// ...

// 把新的通讯录写回磁盘。
out, err := proto.Marshal(book)
if err != nil {
    log.Fatalln("Failed to encode address book:", err)
}
if err := ioutil.WriteFile(fname, out, 0644); err != nil {
    log.Fatalln("Failed to write address book:", err)
}
```

## 读取消息 {#reading-a-message}

要解析已编码的消息，你使用 `proto` 库的 [Unmarshal](https://pkg.go.dev/google.golang.org/protobuf/proto?tab=doc#Unmarshal) 函数。调用该函数时，`in` 中的数据会被当作 Protobuf 消息进行解析，结果放入 `book`。因此，要解析 [`list_people` 命令](https://github.com/protocolbuffers/protobuf/blob/master/examples/go/cmd/list_people/list_people.go)中的文件，我们使用：

```go
// 读取现有的通讯录。
in, err := ioutil.ReadFile(fname)
if err != nil {
    log.Fatalln("Error reading file:", err)
}
book := &pb.AddressBook{}
if err := proto.Unmarshal(in, book); err != nil {
    log.Fatalln("Failed to parse address book:", err)
}
```

## 扩展 Protobuf 消息 {#extending-a-protobuf}

在你发布（release）使用 Protobuf 消息的代码之后，你迟早会想“改进”消息的定义。如果你希望新消息向后兼容（backwards-compatible）、旧消息向前兼容（forward-compatible）——你几乎肯定希望如此——那么需要遵守一些规则。在消息的新版本中：

-   你*不得*更改任何现有字段的字段编号。
-   你*可以*删除字段。
-   你*可以*添加新字段，但必须使用全新的字段编号（也就是说，这些编号在此消息中从未被使用过，连已删除字段用过的也不行）。

（这些规则有[一些例外](/programming-guides/proto3#updating)，但极少使用。）

只要遵守这些规则，旧代码就能顺利读取新消息，并直接忽略所有新字段。对旧代码而言，被删除的单数（singular）字段只会呈现其默认值，被删除的 repeated 字段则为空。新代码也能透明地读取旧消息。

不过请记住，旧消息中不会包含新字段，因此你需要对默认值做合理的处理。这里使用的是类型相关的[默认值](/programming-guides/proto3#default)：字符串的默认值是空字符串，布尔类型的默认值是 false，数值类型的默认值是 0。

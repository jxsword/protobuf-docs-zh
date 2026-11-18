+++
title = "C# 生成代码指南"
weight = 550
linkTitle = "生成代码指南"
description = "描述 Protobuf 编译器针对采用版次（edition）语法的协议定义确切生成哪些 C# 代码。"
type = "docs"
source_url = "https://protobuf.dev/reference/csharp/csharp-generated/"
upstream_commit = "f72a6a648b34e9e098cbce1519bc9c8139105d66"
translated_at = "2026-11-19"
status = "translated"
translator = "agent"
+++

阅读本文档之前，请先阅读 [proto2 语言指南（language guide）](/programming-guides/proto2)、[proto3 语言指南](/programming-guides/proto3)或 [版次（edition）语言指南](/programming-guides/editions)。

## 编译器调用 {#invocation}

使用 `--csharp_out` 命令行标志调用时，Protobuf 编译器会生成 C# 输出。`--csharp_out` 选项（option）的参数是你希望编译器写入 C# 输出的目录；不过，根据[其他选项](#compiler_options)的设置，编译器也可能在指定目录下创建子目录。编译器会为每个输入的 `.proto` 文件创建单个源文件，默认扩展名为 `.cs`，但可通过编译器选项进行配置。

### C# 专属选项 {#compiler_options}

你可以使用 `--csharp_opt` 命令行标志为 Protobuf 编译器提供更多 C# 选项。支持的选项如下：

-   **file_extension**：为生成代码（generated code）设置文件扩展名。默认值为 `.cs`，但常用的替代值是 `.g.cs`，用以表明该文件包含生成代码。

-   **base_namespace**：指定此选项时，生成器会为生成的源代码创建一个目录层级，与生成类的命名空间（namespace）相对应，并使用该选项的值指明命名空间的哪一部分应视为输出目录的“基”。例如，使用如下命令行：

    ```shell
    protoc --proto_path=bar --csharp_out=src --csharp_opt=base_namespace=Example player.proto
    ```

    若 `player.proto` 的 `csharp_namespace` 选项为 `Example.Game`，Protobuf 编译器会生成文件 `src/Game/Player.cs`。此选项通常对应 Visual Studio 中 C# 项目的**默认命名空间（default namespace）**选项。如果指定了该选项但值为空，则会使用生成文件中所用的完整 C# 命名空间来构建目录层级。如果完全未指定该选项，生成的文件会直接写入 `--csharp_out` 指定的目录，不会创建任何层级。

-   **internal_access**：指定此选项时，生成器会使用 `internal` 访问修饰符（而非 `public`）来创建类型。

-   **serializable**：指定此选项时，生成器会为生成的消息（message）类添加 `[Serializable]` 特性（attribute）。

多个选项可以用逗号分隔后一并指定，如下例所示：

```shell
protoc --proto_path=src --csharp_out=build/gen --csharp_opt=file_extension=.g.cs,base_namespace=Example,internal_access src/foo.proto
```

## 文件结构 {#structure}

输出文件的名称由 `.proto` 文件名派生而来：将文件名转换为 Pascal-case 形式，并以下划线作为单词分隔符。例如，名为 `player_record.proto` 的文件会生成名为 `PlayerRecord.cs` 的输出文件（文件扩展名可通过 `--csharp_opt` 指定，[如上文所示](#compiler_options)）。

就公开成员而言，每个生成的文件都采用如下形式。（此处未展示具体实现。）

```csharp
namespace [...]
{
  public static partial class [... descriptor class name ...]
  {
    public static FileDescriptor Descriptor { get; }
  }

  [... Enums ...]
  [... Message classes ...]
}
```

`namespace` 根据 proto 的 `package` 推导得出，所用的转换规则与文件名相同。例如，proto 包（package）为 `example.high_score` 时，得到的命名空间就是 `Example.HighScore`。你可以使用 `csharp_namespace` [文件选项（file option）](/programming-guides/proto3#options)为特定的 .proto 文件覆盖默认生成的命名空间。

每个顶层枚举（enum）和消息都会生成一个对应的枚举或类，并声明为该命名空间的成员。此外，编译器总会为文件描述符（file descriptor）生成一个静态分部类（partial class），用于基于反射（reflection）的操作。描述符类的名称与文件相同（不含扩展名）。不过，如果存在同名的消息（这种情况相当常见），描述符类会被置于嵌套的 `Proto` 命名空间中，以免与该消息冲突。

作为上述各项规则的综合示例，我们来看 Protobuf 自带的 `timestamp.proto` 文件。下面是它的一个精简版本：

```proto
edition = "2023";

package google.protobuf;
option csharp_namespace = "Google.Protobuf.WellKnownTypes";

message Timestamp { ... }
```

生成的 `Timestamp.cs` 文件具有如下结构：

```csharp
namespace Google.Protobuf.WellKnownTypes
{
  namespace Proto
  {
    public static partial class Timestamp
    {
      public static FileDescriptor Descriptor { get; }
    }
  }

  public sealed partial class Timestamp : IMessage<Timestamp>
  {
    [...]
  }
}
```

## 消息 {#message}

给定一个简单的消息声明：

```proto
message Foo {}
```

Protobuf 编译器会生成一个名为 `Foo` 的 sealed 分部类，它实现了 `IMessage<Foo>` 接口，如下所示（含成员声明）。更多信息请参见其中的行内注释。

```csharp
public sealed partial class Foo : IMessage<Foo>
{
  // 用于解析与反射的静态属性
  public static MessageParser<Foo> Parser { get; }
  public static MessageDescriptor Descriptor { get; }

  // IMessage.Descriptor 的显式接口实现，以避免与静态 Descriptor 属性冲突。
  // 通常在引用编译期已知的类型时使用静态属性，而在引用任意消息（例如在
  // JSON 序列化过程中）时使用实例属性。
  MessageDescriptor IMessage.Descriptor { get; }

  // 无参构造函数；如果提供了 OnConstruction 分部方法，则会调用它。
  public Foo();
  // 深拷贝构造函数
  public Foo(Foo);
  // 分部方法，可在同一个类的手写代码中实现，为每当构造实例时
  // 需要运行的代码提供一个挂钩。
  partial void OnConstruction();

  // IDeepCloneable<T>.Clone() 的实现；创建此消息的深拷贝。
  public Foo Clone();

  // 标准相等性处理；注意 IMessage<T> 扩展自 IEquatable<T>
  public override bool Equals(object other);
  public bool Equals(Foo other);
  public override int GetHashCode();

  // 将消息转换为 JSON 表示形式
  public override string ToString();

  // 将消息序列化为 protobuf 二进制格式
  public void WriteTo(CodedOutputStream output);
  // 计算消息在 protobuf 二进制格式下的大小
  public int CalculateSize();

  // 将给定消息的内容合并到此消息中。通常由生成代码和消息解析器使用。
  public void MergeFrom(Foo other);

  // 将给定的 protobuf 二进制格式流的内容合并到此消息中。
  // 通常由生成代码和消息解析器使用。
  public void MergeFrom(CodedInputStream input);
}
```

请注意，所有这些成员始终都会存在；`optimize_for` 选项不会影响 C# 代码生成器（code generator）的输出。

### 嵌套类型

消息可以声明在另一个消息内部。例如：

```proto
message Foo {
  message Bar {
  }
}
```

在这种情况下——或者当消息包含嵌套枚举时——编译器会生成一个嵌套的 `Types` 类，然后在 `Types` 类内部再生成一个 `Bar` 类，因此完整的生成代码如下：

```csharp
namespace [...]
{
  public sealed partial class Foo : IMessage<Foo>
  {
    public static partial class Types
    {
      public sealed partial class Bar : IMessage<Bar> { ... }
    }
  }
}
```

虽然这个中间层 `Types` 类不太便利，但它是必需的：嵌套类型（nested type）在消息中拥有对应字段（field）是一个常见场景，必须用它来应对。否则，同一个类中会出现同名的一个属性和一个类型——而这是 C# 所不允许的。

## 字段

Protobuf 编译器会为消息中定义的每个字段生成一个 C# 属性。属性的确切形态取决于字段的性质：其类型，以及它是单数（singular）、repeated 还是 map 字段。

### 单数字段 {#singular}

任何单数字段都会生成一个可读可写属性。为 `string` 或 `bytes` 字段指定 null 值会抛出 `ArgumentNullException`；从尚未被显式设置的字段取值会返回空字符串或 `ByteString`。消息字段可以设置为 null 值，这实际上等同于清除该字段。但这并不等同于把值设置为消息类型的某个“空”实例。

### repeated 字段 {#repeated}

每个 repeated 字段都会生成一个类型为 `Google.Protobuf.Collections.RepeatedField<T>` 的只读属性，其中 `T` 是字段的元素类型。在大多数情况下，它的行为如同 `List<T>`，但额外提供了一个 `Add` 重载，允许一次性添加一组元素。在对象初始化器（object initializer）中填充 repeated 字段时，这一点非常方便。此外，`RepeatedField<T>` 直接支持序列化（serialization）、反序列化（deserialization）和克隆，不过这些功能通常由生成代码使用，而非手写的应用程序代码。

repeated 字段不能包含 null 值，即使是消息类型也不例外，但[下文解释](#wrapper_types)的可空包装器类型（nullable wrapper types）除外。

### map 字段 {#map}

每个 map 字段都会生成一个类型为 `Google.Protobuf.Collections.MapField<TKey, TValue>` 的只读属性，其中 `TKey` 是字段的键（key）类型，`TValue` 是字段的值（value）类型。在大多数情况下，它的行为如同 `Dictionary<TKey, TValue>`，但额外提供了一个 `Add` 重载，允许一次性添加另一个字典。在对象初始化器中填充 repeated 字段时，这一点同样很方便。此外，`MapField<TKey, TValue>` 直接支持序列化、反序列化和克隆，不过这些功能通常由生成代码使用，而非手写的应用程序代码。map 中的键不允许为 null；如果对应的单数字段类型支持 null 值，则值可以为 null。

### oneof 字段 {#oneof}

oneof 中的每个字段都有一个独立的属性，与普通的[单数字段](#singular)类似。不过，编译器还会额外生成一个属性，用于确定枚举中哪个字段已被设置，同时还会生成一个枚举和一个用于清除该 oneof 的方法。例如，对于以下 oneof 字段定义：

```proto
oneof avatar {
  string image_url = 1;
  bytes image_data = 2;
}
```

编译器会生成以下公开成员：

```csharp
enum AvatarOneofCase
{
  None = 0,
  ImageUrl = 1,
  ImageData = 2
}

public AvatarOneofCase AvatarCase { get; }
public void ClearAvatar();
public string ImageUrl { get; set; }
public ByteString ImageData { get; set; }
```

如果某属性是当前 oneof 的“case”，获取该属性会返回为它设置的值；否则，获取该属性会返回其类型的默认值（default value）——同一时间一个 oneof 中只能设置一个成员。

设置 oneof 的任何一个成员属性都会改变该 oneof 所报告的“case”。与普通的[单数字段](#singular)一样，你不能把 `string` 或 `bytes` 类型的 oneof 字段设置为 null。把消息类型字段设置为 null 等同于调用该 oneof 专属的 `Clear` 方法。

### 包装器类型字段 {#wrapper_types}

大多数知名类型（well-known types）不影响代码生成，但包装器类型（wrapper types，例如 `StringWrapper` 和 `Int32Wrapper`）会改变属性的类型和行为。

对应 C# 值类型的所有包装器类型（例如 `Int32Wrapper`、`DoubleWrapper` 和 `BoolWrapper`）都会映射为 `Nullable<T>`，其中 `T` 是对应的非可空类型。例如，`DoubleValue` 类型的字段会生成 `Nullable<double>` 类型的 C# 属性。

`StringWrapper` 或 `BytesWrapper` 类型的字段会生成 `string` 和 `ByteString` 类型的 C# 属性，但其默认值为 null，并且允许将 null 设置为属性值。

对所有包装器类型而言，repeated 字段中都不允许出现 null 值，但 map 条目的值允许为 null。

## 枚举 {#enum}

给定如下枚举定义：

```proto
enum Color {
  COLOR_UNSPECIFIED = 0;
  COLOR_RED = 1;
  COLOR_GREEN = 5;
  COLOR_BLUE = 1234;
}
```

Protobuf 编译器会生成一个名为 `Color` 的 C# 枚举类型，其取值集合与原定义相同。枚举值的名称会被转换，使其对 C# 开发者来说更加符合习惯：

-   如果原名称以枚举名称本身的大写形式开头，则该部分会被移除
-   随后将结果转换为 Pascal-case 形式

因此，上面的 `Color` proto 枚举会变成如下 C# 代码：

```csharp
enum Color
{
  Unspecified = 0,
  Red = 1,
  Green = 5,
  Blue = 1234
}
```

此名称转换不会影响消息的 JSON 表示形式中所用的文本。

请注意，`.proto` 语言允许多个枚举符号具有相同的数值。数值相同的符号互为同义词。它们在 C# 中的表示方式完全一致：多个名称对应同一个数值。

非嵌套的枚举会生成一个作为命名空间新成员的 C# 枚举；嵌套的枚举则会在与该枚举所嵌套的消息对应的类内部的 `Types` 嵌套类中生成 C# 枚举。

## 服务 {#service}

C# 代码生成器会完全忽略服务（service）。

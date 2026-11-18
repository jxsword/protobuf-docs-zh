+++
title = "Protobuf 基础：Java"
weight = 250
linkTitle = "Java"
description = "面向 Java 程序员的 Protobuf 使用基础入门。"
type = "docs"
source_url = "https://protobuf.dev/getting-started/javatutorial/"
upstream_commit = "f72a6a648b34e9e098cbce1519bc9c8139105d66"
translated_at = "2026-11-19"
status = "translated"
translator = "agent"
+++

本教程为 Java 程序员提供使用 Protobuf 的基础入门，并通过逐步创建一个简单的示例应用，向你展示如何：

-   在 `.proto` 文件中定义消息（message）格式。
-   使用 Protobuf 编译器。
-   使用 Java Protobuf API 写入和读取消息。

本文并不是一份在 Java 中使用 Protobuf 的全面指南。如需更详细的参考信息，请参阅 [Protobuf 语言指南（proto2）](/programming-guides/proto2)、[Protobuf 语言指南（proto3）](/programming-guides/proto3)、[Java API 参考](/reference/java/api-docs/overview-summary.html)、[Java 生成代码指南](/reference/java/java-generated)以及[编码参考](/programming-guides/encoding)。

## 问题域 {#problem-domain}

我们要使用的示例是一个非常简单的“通讯录”应用，它可以把人们的联系信息写入文件，也可以从文件中读出。通讯录中的每个人都有姓名、ID、电子邮件地址和联系电话。

如何对这样的结构化数据（structured data）进行序列化（serialization）并读取出来？有以下几种解决办法：

-   使用 Java 序列化（Serialization）。由于它内置于语言之中，这是一种默认做法，但它有一大堆众所周知的问题（参见 Josh Bloch 所著《Effective Java》第 213 页），而且如果你需要与用 C++ 或 Python 编写的应用共享数据，它的表现也不太好。
-   你可以自行发明一种临时方式，把各数据项编码进单个字符串——例如把 4 个整数编码成“12:3:-23:67”。这种方式简单而灵活，但需要专门编写一次性的编码与解析（parse）代码，而且解析会带来少量运行时开销。它最适合用于编码非常简单的数据。
-   将数据序列化为 XML。这种方式颇具吸引力，因为 XML（勉强）算是人类可读的，而且许多语言都有绑定库。如果你希望与其他应用/项目共享数据，这可能是个不错的选择。然而，XML 以极度占用空间而著称，对其进行编码/解码可能给应用带来巨大的性能损失。此外，遍历 XML DOM 树通常也比访问类中的简单字段（field）复杂得多。

除了这些方案之外，你还可以使用 Protobuf。Protobuf 正是为解决这一问题而生的灵活、高效、自动化方案。使用 Protobuf 时，你要为想要存储的数据结构编写一份 `.proto` 描述。Protobuf 编译器会据此创建一个类，以高效的二进制格式（binary format）实现 Protobuf 数据的自动编码与解析。生成的类为构成 Protobuf 消息的字段提供 getter 和 setter，并负责把消息作为一个整体进行读写时的各项细节。重要的是，Protobuf 格式支持随时间推移扩展格式，同时代码仍能读取以旧格式编码的数据。

## 在哪里找到示例代码 {#example-code}

示例代码包含在源码包中，位于“examples”目录下。[在此下载。](/downloads)

## 定义你的协议格式 {#protocol-format}

要创建你的通讯录应用，需要先从一个 `.proto` 文件开始。`.proto` 文件中的定义很简单：为每个想要序列化的数据结构添加一个*消息*，然后为消息中的每个字段指定名称和类型。下面就是定义你的消息的 `.proto` 文件，即 `addressbook.proto`。

```proto
syntax = "proto2";

package tutorial;

option java_multiple_files = true;
option java_package = "com.example.tutorial.protos";
option java_outer_classname = "AddressBookProtos";

message Person {
  optional string name = 1;
  optional int32 id = 2;
  optional string email = 3;

  enum PhoneType {
    PHONE_TYPE_UNSPECIFIED = 0;
    PHONE_TYPE_MOBILE = 1;
    PHONE_TYPE_HOME = 2;
    PHONE_TYPE_WORK = 3;
  }

  message PhoneNumber {
    optional string number = 1;
    optional PhoneType type = 2 [default = PHONE_TYPE_HOME];
  }

  repeated PhoneNumber phones = 4;
}

message AddressBook {
  repeated Person people = 1;
}
```

可以看到，其语法与 C++ 或 Java 相似。下面我们逐部分过一遍这个文件，看看各部分的作用。

`.proto` 文件以一条 package 声明开头，这有助于避免不同项目之间的命名冲突。在 Java 中，除非你像本例中这样显式指定了 `java_package`，否则 package 名称会被直接用作 Java 包。即使你提供了 `java_package`，也仍然应当定义一个普通的 `package`，以避免在 Protobuf 命名空间（namespace）以及非 Java 语言中发生名称冲突。

package 声明之后，可以看到三个 Java 特有的选项（option）：`java_multiple_files`、`java_package` 和 `java_outer_classname`。`java_package` 指定生成的类应当归属于哪个 Java 包名。如果不显式指定，它会直接沿用 `package` 声明给出的包名，但这些名称通常不是合适的 Java 包名（因为它们通常不以域名开头）。`java_outer_classname` 选项定义代表该文件的包装类的类名。如果不显式给出 `java_outer_classname`，系统会把文件名转换为大驼峰形式来生成它。例如，“my_proto.proto” 默认会使用 “MyProto” 作为包装类名。`java_multiple_files = true` 选项会为每个生成的类各生成一个单独的 `.java` 文件（而不是旧有的行为：为包装类生成单个 `.java` 文件，将包装类用作外部类，并把所有其他类嵌套在该包装类之中）。

接下来是消息定义。消息只是一个包含一组带类型字段的聚合体（aggregate）。许多标准简单数据类型都可用作字段类型，包括 `bool`、`int32`、`float`、`double` 和 `string`。你还可以把其他消息类型用作字段类型，为消息添加更深层的结构——在上面的示例中，`Person` 消息包含 `PhoneNumber` 消息，而 `AddressBook` 消息包含 `Person` 消息。你甚至可以把消息类型嵌套定义在其他消息内部——如你所见，`PhoneNumber` 类型就定义在 `Person` 之中。如果希望某个字段的取值限定在一组预定义值之内，你还可以定义枚举（enum）类型——这里的目的是指定电话号码可以是 `PHONE_TYPE_MOBILE`、`PHONE_TYPE_HOME` 或 `PHONE_TYPE_WORK` 这几种电话类型之一。

每个元素上的 “ = 1”、“ = 2” 标记，标识出该字段在二进制编码中使用的唯一“标签”（tag）。字段编号 1-15 比更大的编号少用一个字节来编码，因此作为一种优化，你可以决定把 1-15 这些编号用于常用或可重复（repeated）的元素，而把 16 及以上的编号留给不那么常用的 optional 元素。repeated 字段中的每个元素都需要重新编码字段编号，因此 repeated 字段尤其适合采用这种优化。

每个字段都必须标注以下修饰符之一：

-   `optional`：字段可以设置，也可以不设置。如果 optional 字段的值未设置，就会使用默认值（default value）。对于简单类型，你可以指定自己的默认值，就像示例中电话号码的 `type` 字段那样；否则将使用系统默认值：数值类型为 0，字符串为空字符串，布尔类型为 false。对于内嵌消息，默认值始终是该消息的“默认实例”或“原型（prototype）”，也就是一个没有任何字段被设置的消息。调用访问器（accessor）获取一个未显式设置的 optional（或 required）字段的值时，返回的总是该字段的默认值。
-   `repeated`：字段可以重复任意多次（包括零次）。重复值的顺序会在 Protobuf 消息中得到保留。可以把 repeated 字段看作大小动态可变的数组。
-   `required`：必须为字段提供一个值，否则该消息将被视为“未初始化”。尝试构建未初始化的消息会抛出 `RuntimeException`。解析未初始化的消息会抛出 `IOException`。除此之外，required 字段的行为与 optional 字段完全相同。

{{% alert title="Important" color="warning" %}} **required 是永久的**
把字段标记为 `required` 时务必非常谨慎。如果将来某个时候你希望停止写入或发送某个 required 字段，再把它改成 optional 字段就会很成问题——旧读取代码会把缺少该字段的消息视为不完整，并可能无意中拒绝或丢弃它们。作为替代，你可以考虑为自己的数据编写应用特定的自定义校验例程。在 Google 内部，`required` 字段极不受欢迎；以 proto2 语法定义的大多数消息只使用 `optional` 和 `repeated`。（proto3 则完全不支持 `required` 字段。）
{{% /alert %}}

关于编写 `.proto` 文件的完整指南——包括所有可能的字段类型——请参阅 [Protobuf 语言指南](/programming-guides/proto2)。不过，不要去找类似类继承的机制——Protobuf 并不支持这种做法。

## 编译你的 Protobuf 模式（schema）{#compiling-protocol-buffers}

现在你已经有 `.proto` 文件了，接下来要做的就是生成读写 `AddressBook`（因而也包括 `Person` 和 `PhoneNumber`）消息所需的类。为此，你需要用 Protobuf 编译器 `protoc` 编译你的 `.proto`：

1.  如果尚未安装编译器，请[下载安装包](/downloads)，并按照 README 中的说明操作。

1.  现在运行编译器，指定源目录（你的应用源码所在的位置——如果未提供该值，则使用当前目录）、目标目录（希望生成的代码存放的位置；通常与 `$SRC_DIR` 相同），以及你的 `.proto` 的路径。在本例中，应执行以下命令：

    ```shell
    protoc -I=$SRC_DIR --java_out=$DST_DIR $SRC_DIR/addressbook.proto
    ```

    由于你想要的是 Java 类，因此要使用 `--java_out` 选项——其他受支持的语言也提供了类似的选项。

这会在你指定的目标目录中生成一个 `com/example/tutorial/protos/` 子目录，其中包含几个生成的 `.java` 文件。

## Protobuf API {#protobuf-api}

我们来看看部分生成代码，了解一下编译器为你创建了哪些类和方法。打开 `com/example/tutorial/protos/` 目录可以看到，其中包含若干 `.java` 文件，为你在 `addressbook.proto` 中指定的每个消息各定义了一个类。每个类都有自己配套的 `Builder` 类，你可以用它来创建该类的实例。关于构建器（builder）的更多信息，请参阅下文的[构建器与消息](#builders-messages)一节。

消息和构建器都会为消息的每个字段自动生成访问器方法；消息只有 getter，而构建器既有 getter 也有 setter。下面是 `Person` 类的部分访问器（为简洁起见省略了实现）：

```java
// required string name = 1;
public boolean hasName();
public String getName();

// required int32 id = 2;
public boolean hasId();
public int getId();

// optional string email = 3;
public boolean hasEmail();
public String getEmail();

// repeated .tutorial.Person.PhoneNumber phones = 4;
public List<PhoneNumber> getPhonesList();
public int getPhonesCount();
public PhoneNumber getPhones(int index);
```

与此同时，`Person.Builder` 则拥有相同的 getter 外加 setter：

```java
// required string name = 1;
public boolean hasName();
public String getName();
public Builder setName(String value);
public Builder clearName();

// required int32 id = 2;
public boolean hasId();
public int getId();
public Builder setId(int value);
public Builder clearId();

// optional string email = 3;
public boolean hasEmail();
public String getEmail();
public Builder setEmail(String value);
public Builder clearEmail();

// repeated .tutorial.Person.PhoneNumber phones = 4;
public List<PhoneNumber> getPhonesList();
public int getPhonesCount();
public PhoneNumber getPhones(int index);
public Builder setPhones(int index, PhoneNumber value);
public Builder addPhones(PhoneNumber value);
public Builder addAllPhones(Iterable<PhoneNumber> value);
public Builder clearPhones();
```

可以看到，每个字段都有简单的 JavaBeans 风格 getter 和 setter。每个单数（singular）字段还有对应的 `has` getter——如果该字段已被设置，它们会返回 true。最后，每个字段都有一个 `clear` 方法，用于把字段重新置回未设置的空状态。

repeated 字段还有一些额外的方法——一个 `Count` 方法（只是列表大小的简写形式）、按索引获取或设置列表中特定元素的 getter 和 setter、向列表追加新元素的 `add` 方法，以及把装满元素的整个容器加入列表的 `addAll` 方法。

请注意，尽管 `.proto` 文件使用小写加下划线的形式，这些访问器方法却采用驼峰式命名。这一转换由 Protobuf 编译器自动完成，使生成的类符合标准的 Java 风格约定。在 `.proto` 文件中，字段名（field name）应始终使用小写加下划线的形式；这能确保所有生成语言中的命名都符合良好实践。关于良好的 `.proto` 风格的更多内容，请参阅[样式指南](/programming-guides/style)。

关于协议编译器针对任何特定字段定义究竟会生成哪些成员的详细信息，请参阅 [Java 生成代码参考](/reference/java/java-generated)。

### 枚举与嵌套类 {#enums-nested-classes}

生成代码中包含一个 `PhoneType` Java 5 枚举，嵌套在 `Person` 之中：

```java
public static enum PhoneType {
  PHONE_TYPE_UNSPECIFIED(0, 0),
  PHONE_TYPE_MOBILE(1, 1),
  PHONE_TYPE_HOME(2, 2),
  PHONE_TYPE_WORK(3, 3),
  ;
  ...
}
```

正如你所期望的，嵌套类型（nested type）`Person.PhoneNumber` 会生成为 `Person` 内部的一个嵌套类。

### 构建器与消息 {#builders-messages}

Protobuf 编译器生成的消息类都是*不可变的*（immutable）。消息对象一旦构建完成，就无法再修改，就像 Java 的 `String` 一样。要构建一条消息，你必须先构建一个构建器，把想设置的字段设置为你选定的值，然后调用该构建器的 `build()` 方法。

你可能已经注意到，构建器中每个会修改消息的方法都会返回另一个构建器。返回的对象实际上就是你调用该方法时所用的同一个构建器。这样做只是为了方便，让你能把多个 setter 串接在同一行代码中。

下面是创建 `Person` 实例的一个示例：

```java
Person john =
  Person.newBuilder()
    .setId(1234)
    .setName("John Doe")
    .setEmail("jdoe@example.com")
    .addPhones(
      Person.PhoneNumber.newBuilder()
        .setNumber("555-4321")
        .setType(Person.PhoneType.PHONE_TYPE_HOME)
        .build());
    .build();
```

### 标准消息方法 {#standard-message-methods}

每个消息类和构建器类还包含许多其他方法，可用于检查或操作整个消息，包括：

-   `isInitialized()`：检查是否所有 required 字段都已设置。
-   `toString()`：返回消息的人类可读表示形式，对调试特别有用。
-   `mergeFrom(Message other)`：（仅构建器）把 `other` 的内容合并进当前消息——覆盖单数标量（scalar）字段、合并复合字段、拼接 repeated 字段。
-   `clear()`：（仅构建器）把所有字段清空回空状态。

这些方法实现的是所有 Java 消息和构建器共享的 `Message` 与 `Message.Builder` 接口。更多信息请参阅 [`Message` 的完整 API 文档](/reference/java/api-docs/com/google/protobuf/Message.html)。

### 解析与序列化 {#parsing-serialization}

最后，每个 Protobuf 类都有一些方法，用于通过 Protobuf [二进制格式](/programming-guides/encoding)写入和读取你所选类型的消息。这些方法包括：

-   `byte[] toByteArray();`：序列化该消息，并返回一个包含其原始字节的字节数组。
-   `static Person parseFrom(byte[] data);`：从给定的字节数组解析出一条消息。
-   `void writeTo(OutputStream output);`：序列化该消息，并将其写入 `OutputStream`。
-   `static Person parseFrom(InputStream input);`：从 `InputStream` 读取并解析出一条消息。

这些只是用于解析和序列化的众多选项中的几个。完整列表请参阅 [`Message` API 参考](/reference/java/api-docs/com/google/protobuf/Message.html)。

{{% alert title="Important" color="warning" %}} **Protobuf 与面向对象设计**
Protobuf 类基本上只是数据载体（类似于 C 语言中的 struct），并不提供额外的功能；在对象模型中，它们并不适合作为一等公民。如果你想为生成的类添加更丰富的行为，最好的做法是把生成的 Protobuf 类包装在一个应用特定的类中。如果你无法控制 `.proto` 文件的设计（例如你在复用另一个项目的文件），把 Protobuf 消息包装起来也是个好主意。在这种情况下，你可以利用包装类来打造一个更适合你的应用独特环境的接口：隐藏部分数据和方法、暴露便捷函数等等。**你绝不应该通过继承生成的类来为其添加行为**。这样做会破坏内部机制，而且本来也不符合良好的面向对象实践。 {{% /alert %}}

## 写入消息 {#writing-a-message}

现在我们来试用你的 Protobuf 类。你希望通讯录应用实现的第一件事，就是把个人信息写入通讯录文件。为此，你需要创建并填充 Protobuf 类的实例，然后把它们写入输出流。

下面这个程序会从文件中读取 `AddressBook`，根据用户输入向其中添加一个新的 `Person`，然后把新的 `AddressBook` 重新写回文件。其中直接调用或引用协议编译器所生成代码的部分已突出显示。

```java
import com.example.tutorial.protos.AddressBook;
import com.example.tutorial.protos.Person;
import java.io.BufferedReader;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.InputStreamReader;
import java.io.IOException;
import java.io.PrintStream;

class AddPerson {
  // 此函数根据用户输入填充一条 Person 消息。
  static Person PromptForAddress(BufferedReader stdin,
                                 PrintStream stdout) throws IOException {
    Person.Builder person = Person.newBuilder();

    stdout.print("Enter person ID: ");
    person.setId(Integer.valueOf(stdin.readLine()));

    stdout.print("Enter name: ");
    person.setName(stdin.readLine());

    stdout.print("Enter email address (blank for none): ");
    String email = stdin.readLine();
    if (email.length() > 0) {
      person.setEmail(email);
    }

    while (true) {
      stdout.print("Enter a phone number (or leave blank to finish): ");
      String number = stdin.readLine();
      if (number.length() == 0) {
        break;
      }

      Person.PhoneNumber.Builder phoneNumber =
        Person.PhoneNumber.newBuilder().setNumber(number);

      stdout.print("Is this a mobile, home, or work phone? ");
      String type = stdin.readLine();
      if (type.equals("mobile")) {
        phoneNumber.setType(Person.PhoneType.PHONE_TYPE_MOBILE);
      } else if (type.equals("home")) {
        phoneNumber.setType(Person.PhoneType.PHONE_TYPE_HOME);
      } else if (type.equals("work")) {
        phoneNumber.setType(Person.PhoneType.PHONE_TYPE_WORK);
      } else {
        stdout.println("Unknown phone type.  Using default.");
      }

      person.addPhones(phoneNumber);
    }

    return person.build();
  }

  // main 函数：从文件中读取整个通讯录，
  //   根据用户输入添加一个人，然后把结果写回同一个文件。
  public static void main(String[] args) throws Exception {
    if (args.length != 1) {
      System.err.println("Usage:  AddPerson ADDRESS_BOOK_FILE");
      System.exit(-1);
    }

    AddressBook.Builder addressBook = AddressBook.newBuilder();

    // 读取现有的通讯录。
    try {
      addressBook.mergeFrom(new FileInputStream(args[0]));
    } catch (FileNotFoundException e) {
      System.out.println(args[0] + ": File not found.  Creating a new file.");
    }

    // 添加一条地址。
    addressBook.addPeople(
      PromptForAddress(new BufferedReader(new InputStreamReader(System.in)),
                       System.out));

    // 把新的通讯录写回磁盘。
    FileOutputStream output = new FileOutputStream(args[0]);
    addressBook.build().writeTo(output);
    output.close();
  }
}
```

## 读取消息 {#reading-a-message}

当然，如果无法从中取出任何信息，通讯录就没多大用处了！本示例读取由上一个示例创建的文件，并打印其中的所有信息。

```java
import com.example.tutorial.protos.AddressBook;
import com.example.tutorial.protos.Person;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.PrintStream;

class ListPeople {
  // 遍历 AddressBook 中的所有人并打印他们的信息。
  static void Print(AddressBook addressBook) {
    for (Person person: addressBook.getPeopleList()) {
      System.out.println("Person ID: " + person.getId());
      System.out.println("  Name: " + person.getName());
      if (person.hasEmail()) {
        System.out.println("  E-mail address: " + person.getEmail());
      }

      for (Person.PhoneNumber phoneNumber : person.getPhonesList()) {
        switch (phoneNumber.getType()) {
          case PHONE_TYPE_MOBILE:
            System.out.print("  Mobile phone #: ");
            break;
          case PHONE_TYPE_HOME:
            System.out.print("  Home phone #: ");
            break;
          case PHONE_TYPE_WORK:
            System.out.print("  Work phone #: ");
            break;
        }
        System.out.println(phoneNumber.getNumber());
      }
    }
  }

  // main 函数：从文件中读取整个通讯录，并打印其中的全部信息。
  public static void main(String[] args) throws Exception {
    if (args.length != 1) {
      System.err.println("Usage:  ListPeople ADDRESS_BOOK_FILE");
      System.exit(-1);
    }

    // 读取现有的通讯录。
    AddressBook addressBook =
      AddressBook.parseFrom(new FileInputStream(args[0]));

    Print(addressBook);
  }
}
```

## 扩展 Protobuf 消息 {#extending-a-protobuf}

在发布使用你的 Protobuf 消息的代码之后，你迟早会想“改进”消息的定义。如果你希望新消息向后兼容（backward compatibility）、旧消息向前兼容（forward compatibility）——你几乎肯定希望如此——那么就需要遵循一些规则。在新版消息中：

-   *不得*更改任何现有字段的字段编号。
-   *不得*添加或删除任何 required 字段。
-   *可以*删除 optional 或 repeated 字段。
-   *可以*添加新的 optional 或 repeated 字段，但必须使用全新的字段编号（也就是说，这些字段编号在此消息中从未被使用过，即使是被删除的字段用过的也不行）。

（这些规则[存在一些例外](/programming-guides/proto2#updating)，但很少用到。）

只要遵循这些规则，旧代码就能顺利读取新消息，并直接忽略任何新增字段。对旧代码而言，被删除的 optional 字段只会取其默认值，被删除的 repeated 字段则为空。新代码也能透明地读取旧消息。但请记住，旧消息中不会存在新增的 optional 字段，因此你要么用 `has_` 显式检查它们是否已设置，要么在 `.proto` 文件中在字段编号之后用 `[default = value]` 提供一个合理的默认值。如果未为 optional 元素指定默认值，则会改用类型相关的默认值：字符串的默认值是空字符串，布尔类型的默认值是 false，数值类型的默认值是 0。还要注意，如果你新增了一个 repeated 字段，新代码将无法区分它是被（新代码）留空了，还是从未被（旧代码）设置过，因为它没有 `has_` 标志。

## 高级用法 {#advanced-usage}

Protobuf 的用途远不止简单的访问器和序列化。务必探索一下 [Java API 参考](/reference/java/api-docs/index-all.html)，看看用它还能做些什么。

协议消息类提供的一项关键特性是*反射*（reflection）。你可以遍历消息的字段并操作其值，而无需让代码依赖任何具体的消息类型。反射的一个非常有用的用途，是在协议消息与其他编码（例如 XML 或 JSON）之间相互转换。反射更高级的用法，可能是找出同类型的两条消息之间的差异，或者开发某种“协议消息正则表达式”，让你能编写匹配特定消息内容的表达式。只要发挥想象力，Protobuf 能应用到的问题范围会远远超出你最初的预期！

反射作为 [`Message`](/reference/java/api-docs/com/google/protobuf/Message.html) 和 [`Message.Builder`](/reference/java/api-docs/com/google/protobuf/Message.Builder.html) 接口的一部分提供。

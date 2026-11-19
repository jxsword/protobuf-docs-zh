+++
title = "descriptor.pb.h"
toc_hide = "true"
linkTitle = "C++"
description = "本节包含在 C++ 中使用 Protobuf 类的参考文档。"
type = "docs"
source_url = "https://protobuf.dev/reference/cpp/api-docs/google.protobuf.descriptor.pb/"
upstream_commit = "f72a6a648b34e9e098cbce1519bc9c8139105d66"
translated_at = "2026-11-20"
status = "translated"
translator = "agent"
+++

<p><code>#include &lt;google/protobuf/descriptor.pb.h&gt;<br>namespace <a href="#google.protobuf">google::protobuf</a></code></p><p>描述符（descriptor）的 Protobuf 表示。</p><p>本文件在命名空间（namespace）google::protobuf 中定义了一组协议消息（message）类，用于表示与 <a href="google.protobuf.descriptor">descriptor.h</a> 中定义的类相同的信息。你可以使用 <a href="google.protobuf.descriptor#DescriptorPool">DescriptorPool</a> 类将 <a href='#FileDescriptorProto'>FileDescriptorProto</a> 转换为 <a href='google.protobuf.descriptor#FileDescriptor'>FileDescriptor</a>。因此，本文件中的这些类使得协议类型定义（即反射（reflection）机制所使用的描述符数据）能够在进程之间高效地传递。</p>

<p>协议编译器目前不支持自动生成的文档，因此本页不含各定义的描述。本文件由协议编译器根据 <code>descriptor.proto</code> 生成，其中的消息描述了 .proto 文件中的各类定义，如消息（message）、字段（field）、扩展（extension）、服务（service），以及映射条目的键（key）与值（value）。其内容如下：</p>

<pre>// Protocol Buffers - Google 的数据交换格式
// 版权所有 2008 Google Inc.，保留所有权利。
// https://developers.google.com/protocol-buffers/
//
// 在满足以下条件的前提下，允许以源代码和二进制两种形式
// （无论是否修改）再分发和使用本软件：
//
//
//     * 以源代码形式再分发时，必须保留上述版权声明、本条件清单
// 以及下列免责声明。
//     * 以二进制形式再分发时，必须在随分发提供的文档和/或
// 其他材料中复述上述版权声明、本条件清单以及下列
// 免责声明。
//
//     * 未经事先明确的书面许可，不得将 Google Inc. 的名称或其
// 贡献者的名称用于为源自本软件的衍生产品背书或推广。
//
//
// 本软件由版权持有者与贡献者“按原样”提供，不提供任何
// 明示或默示的担保，包括但不限于对适销性和特定用途
// 适用性的默示担保。
// 无论何种情形，版权持有者或贡献者均不对任何直接、间接、
// 偶然、特殊、惩戒性或后果性的损害（包括但不限于替代商品
// 或服务的采购、使用、数据或利润的损失，或营业中断）承担
// 责任，无论该损害因何产生，也无论其属于合同责任、严格
// 责任或侵权责任（包括疏忽或其他情形），即使已被告知
// 发生此类损害的可能性，因使用本软件而产生的任何损害
// 亦概不负责。
//

// 作者：kenton@google.com（Kenton Varda）
//  基于 Sanjay Ghemawat、Jeff Dean 等人设计的
//  原始 Protocol Buffers。
//
// 本文件中的消息描述了 .proto 文件中出现的各项定义。
// 一个合法的 .proto 文件无需任何其他信息即可直接转换为
// FileDescriptorProto（例如无需读取其导入）。

syntax = "proto2";

package google.protobuf;

option go_package = "google.golang.org/protobuf/types/descriptorpb";
option java_package = "com.google.protobuf";
option java_outer_classname = "DescriptorProtos";
option csharp_namespace = "Google.Protobuf.Reflection";
option objc_class_prefix = "GPB";
option cc_enable_arenas = true;

// descriptor.proto 必须针对速度进行优化，因为基于反射
// 的算法在自举（bootstrapping）期间无法工作。
option optimize_for = SPEED;

// 协议编译器可以输出一个 FileDescriptorSet，其中包含它
// 所解析的 .proto 文件。
message FileDescriptorSet {
  repeated FileDescriptorProto file = 1;
}

// 描述一个完整的 .proto 文件。
message FileDescriptorProto {
  optional string name = 1;     // 文件名，相对于源代码树的根目录
  optional string package = 2;  // 例如 "foo"、"foo.bar" 等。

  // 本文件导入的文件的名称。
  repeated string dependency = 3;
  // 上述依赖列表中公共导入（public import）文件的索引。
  repeated int32 public_dependency = 10;
  // 依赖列表中弱导入（weak import）文件的索引。
  // 仅供 Google 内部迁移使用。请勿使用。
  repeated int32 weak_dependency = 11;

  // 本文件中的全部顶层定义。
  repeated DescriptorProto message_type = 4;
  repeated EnumDescriptorProto enum_type = 5;
  repeated ServiceDescriptorProto service = 6;
  repeated FieldDescriptorProto extension = 7;

  optional FileOptions options = 8;

  // 此字段包含关于原始源代码的可选信息。
  // 你可以安全地移除整个字段，而不会损害描述符的运行时
  // 功能——这些信息只有开发工具才需要。
  //
  optional SourceCodeInfo source_code_info = 9;

  // proto 文件的语法。
  // 支持的取值为 "proto2" 和 "proto3"。
  optional string syntax = 12;
}

// 描述一个消息类型。
message DescriptorProto {
  optional string name = 1;

  repeated FieldDescriptorProto field = 2;
  repeated FieldDescriptorProto extension = 6;

  repeated DescriptorProto nested_type = 3;
  repeated EnumDescriptorProto enum_type = 4;

  message ExtensionRange {
    optional int32 start = 1;  // 包含。
    optional int32 end = 2;    // 不包含。

optional ExtensionRangeOptions options = 3;

  }
  repeated ExtensionRange extension_range = 5;

  repeated OneofDescriptorProto oneof_decl = 8;

  optional MessageOptions options = 7;

  // 保留标签（tag）编号的区间。同一消息中的字段或扩展区间
  // 不得使用这些保留标签编号。保留区间之间不得重叠。
  //
  message ReservedRange {
    optional int32 start = 1;  // 包含。
    optional int32 end = 2;    // 不包含。
  }
  repeated ReservedRange reserved_range = 9;
  // 保留的字段名，同一消息中的字段不得使用这些名称。
  // 一个名称只能保留一次。
  repeated string reserved_name = 10;
}

message ExtensionRangeOptions {
  // 解析器会把它无法识别的选项存储在这里。参见上文。
  repeated UninterpretedOption uninterpreted_option = 999;

  // 客户端可以在本消息的扩展中定义自定义选项。参见上文。
  extensions 1000 to max;
}

// 描述消息中的一个字段。
message FieldDescriptorProto {
  enum Type {
    // 0 保留用于错误。
    // 出于历史原因，取值顺序比较奇怪。
    TYPE_DOUBLE = 1;
    TYPE_FLOAT = 2;
    // 不使用 ZigZag 编码。负数会占用 10 个字节。如果可能出现
    // 负值，请使用 TYPE_SINT64。
    TYPE_INT64 = 3;
    TYPE_UINT64 = 4;
    // 不使用 ZigZag 编码。负数会占用 10 个字节。如果可能出现
    // 负值，请使用 TYPE_SINT32。
    TYPE_INT32 = 5;
    TYPE_FIXED64 = 6;
    TYPE_FIXED32 = 7;
    TYPE_BOOL = 8;
    TYPE_STRING = 9;
    // 以标签定界的聚合。
    // 组（group）类型已弃用，proto3 不再支持。不过，proto3 的
    // 实现仍应能够解析组的线路格式（wire format），并将组字段
    // 当作未知字段处理。
    TYPE_GROUP = 10;
    TYPE_MESSAGE = 11;  // 长度限定（length-delimited）的聚合。

// 版本 2 新增。
TYPE_BYTES = 12;
TYPE_UINT32 = 13;
TYPE_ENUM = 14;
TYPE_SFIXED32 = 15;
TYPE_SFIXED64 = 16;
TYPE_SINT32 = 17;  // 使用 ZigZag 编码。
TYPE_SINT64 = 18;  // 使用 ZigZag 编码。

  }

  enum Label {
    // 0 保留用于错误
    LABEL_OPTIONAL = 1;
    LABEL_REQUIRED = 2;
    LABEL_REPEATED = 3;
  }

  optional string name = 1;
  optional int32 number = 3;
  optional Label label = 4;

  // 如果设置了 type_name，则无需设置此字段。如果此字段与
  // type_name 同时设置，则此字段必须是 TYPE_ENUM、TYPE_MESSAGE 或 TYPE_GROUP 之一。
  optional Type type = 5;

  // 对于消息类型和枚举类型，此字段是该类型的名称。如果名称以
  // '.' 开头，则它是完全限定（fully-qualified）名称。否则，将使用
  // 类似 C++ 的作用域规则来查找该类型（即先搜索本消息内的
  // 嵌套类型，再搜索父级，直至根命名空间）。
  //
  optional string type_name = 6;

  // 对于扩展，此字段是被扩展类型的名称。其解析方式与
  // type_name 相同。
  optional string extendee = 2;

  // 对于数值类型，包含该值的原始文本表示。
  // 对于布尔值，为 "true" 或 "false"。
  // 对于字符串，包含默认的文本内容（不做任何转义）。
  // 对于字节串（bytes），包含经 C 转义的值。所有 &gt;= 128 的字节都会被转义。
  optional string default_value = 7;

  // 如果设置，则给出此字段在包含类型的 oneof_decl 列表中
  // 所归属 oneof 的索引。此字段是该 oneof 的成员。
  optional int32 oneof_index = 9;

  // 此字段的 JSON 名称。该值由协议编译器设置。如果用户已在此
  // 字段上设置 "json_name" 选项，则使用该选项的值；否则，通过
  // 把字段名转换为驼峰命名（camelCase）来推导。
  //
  optional string json_name = 10;

  optional FieldOptions options = 8;

  // 如果为 true，则此字段是 proto3 的 "optional"。当 proto3 字段为
  // optional 时，无论字段类型如何，它都会进行存在性追踪。
  //
  // 当 proto3_optional 为 true 时，此字段必须属于某个 oneof，以便向
  // 旧版 proto3 客户端表明此字段会追踪存在性。这个 oneof 被称为
  // "合成（synthetic）" oneof，此字段必须是它的唯一成员（每个 proto3
  // optional 字段都拥有自己的合成 oneof）。合成 oneof 只存在于描述符
  // 中，不会生成任何 API。合成 oneof 必须排在所有“真实” oneof
  // 之后。
  //
  // 对于消息字段，proto3_optional 不会带来任何语义变化，因为非
  // repeated 的消息字段总是追踪存在性。但它仍然表明了用户是否
  // 写出 "optional" 这一语义细节。这对 .proto 文件的往返
  // （round-trip）转换可能有用。为保持一致，我们也为消息字段
  // 提供合成 oneof，尽管追踪存在性并不需要它。这一点尤其重要，
  // 因为解析器无法分辨字段是消息还是枚举，所以它必须始终
  // 创建合成 oneof。
  //
  //
  // proto2 的 optional 字段不设置此标志，因为它们已经通过
  // `LABEL_OPTIONAL` 表明了 optional。
  optional bool proto3_optional = 17;
}

// 描述一个 oneof。
message OneofDescriptorProto {
  optional string name = 1;
  optional OneofOptions options = 2;
}

// 描述一个枚举类型。
message EnumDescriptorProto {
  optional string name = 1;

  repeated EnumValueDescriptorProto value = 2;

  optional EnumOptions options = 3;

  // 保留数值的区间。同一枚举中的枚举项不得使用这些保留数值。
  // 保留区间之间不得重叠。
  //
  // 注意，这与 DescriptorProto.ReservedRange 不同：此处的区间是
  // 包含式的（两端均含），以便恰当地表示整个 int32 取值域。
  //
  message EnumReservedRange {
    optional int32 start = 1;  // 包含。
    optional int32 end = 2;    // 包含。
  }

  // 保留数值的区间。同一枚举声明中的枚举值不得使用这些保留数值。
  // 保留区间之间不得重叠。
  //
  repeated EnumReservedRange reserved_range = 4;

  // 保留的枚举值名称，不得重复使用。一个名称只能保留一次。
  //
  repeated string reserved_name = 5;
}

// 描述枚举中的一个值。
message EnumValueDescriptorProto {
  optional string name = 1;
  optional int32 number = 2;

  optional EnumValueOptions options = 3;
}

// 描述一个服务。
message ServiceDescriptorProto {
  optional string name = 1;
  repeated MethodDescriptorProto method = 2;

  optional ServiceOptions options = 3;
}

// 描述服务中的一个方法。
message MethodDescriptorProto {
  optional string name = 1;

  // 输入与输出类型的名称。它们的解析方式与
  // FieldDescriptorProto.type_name 相同，但必须指向消息类型。
  optional string input_type = 2;
  optional string output_type = 3;

  optional MethodOptions options = 4;

  // 表明客户端是否流式发送多条客户端消息
  optional bool client_streaming = 5 [default = false];
  // 表明服务端是否流式发送多条服务端消息
  optional bool server_streaming = 6 [default = false];
}

// ===================================================================
// 选项

// 上面的每个定义都可以附加“选项”。这些只是注解，可能会使生成的
// 代码略有不同，或者可能为操作协议消息的代码提供提示。
//
//
// 客户端可以把自定义选项定义为 *Options 消息的扩展。在解析时可能
// 还不知道这些扩展，因此解析器无法把值存入其中。解析器会把值
// 存储在 *Options 消息中一个名为 uninterpreted_option 的字段里。
// 此字段在所有 *Options 消息中必须同名。在构建描述符时，我们会
// 用这个字段来填充扩展——此时所有 proto 都已解析完毕，因此所有
// 扩展都是已知的。
//
//
// 自定义选项的扩展编号可按如下方式选取：
// * 对于只在单一应用程序或组织内部使用的选项，或实验性选项，
//   使用字段编号 50000 到 99999。请自行确保不要把同一编号用于
//   多个选项。
//
// * 对于将要发布并供多个独立实体公开使用的选项，请发邮件至
//   protobuf-global-extension-registry@google.com 预订扩展编号。
//   只需提供你的项目名称（例如 Objective-C 插件）和项目网站
//   （如有）——无需说明打算如何使用它们。通常你只需要一个扩展
//   编号。把多个选项放入一个子消息中，就可以只用一个扩展编号
//   声明多个选项。示例参见文档的 Custom Options 一节：
//
//
//   /programming-guides/proto#options
//   如果这种做法流行起来，将会建立一个 Web 服务来自动分配
//   选项编号。

message FileOptions {

  // 设置从此 .proto 生成的类将被放置到的 Java 包。默认使用 proto
  // 包，但这通常不合适，因为 proto 包名一般不以反向域名开头。
  //
  //
  optional string java_package = 1;

  // 控制为此 .proto 文件生成的 Java 包装类的名称。该类将始终包含
  // 此 .proto 文件的 getDescriptor() 方法，以及此 .proto 文件中定义
  // 的所有顶层扩展。
  // 如果禁用 java_multiple_files，则此 .proto 文件中的所有其他类
  // 都会嵌套在这个唯一的包装外部类之中。
  optional string java_outer_classname = 8;

  // 如果启用，则 Java 代码生成器会为 .proto 文件中定义的每个顶层
  // 消息、枚举和服务分别生成一个单独的 .java 文件。因此，这些类型
  // 将 *不会* 嵌套在 java_outer_classname 指定的包装类之中。不过，
  // 包装类仍会生成，用以包含该文件的 getDescriptor() 方法以及文件
  // 中定义的所有顶层扩展。
  //
  optional bool java_multiple_files = 10 [default = false];

  // 此选项已弃用（deprecated），无任何作用。
  optional bool java_generate_equals_and_hash = 20 [deprecated=true];

  // 如果设为 true，则 Java2 代码生成器生成的代码会在尝试把非
  // UTF-8 字节序列赋给字符串字段时抛出异常。
  //
  // 消息反射也会如此。
  // 不过，扩展字段仍然接受非 UTF-8 字节序列。
  // 此选项在搭配 lite 运行时使用时不起作用。
  optional bool java_string_check_utf8 = 27 [default = false];

  // 生成的类可以针对速度或代码体积进行优化。
  enum OptimizeMode {
    SPEED = 1;         // 生成用于解析、序列化等操作的
                       // 完整代码。
    CODE_SIZE = 2;     // 使用 ReflectionOps 实现这些方法。
    LITE_RUNTIME = 3;  // 使用 MessageLite 和 lite 运行时生成代码。
  }
  optional OptimizeMode optimize_for = 9 [default = SPEED];

  // 设置从此 .proto 生成的结构体将被放置到的 Go 包。如果省略，
  // Go 包将按以下来源推导：
  //   - 包导入路径的基名（如果提供了导入路径）。
  //   - 否则，.proto 文件中的 package 语句（如果存在）。
  //   - 否则，.proto 文件名去掉扩展名后的基名。
  optional string go_package = 11;

  // 是否应在每种语言中生成通用服务？“通用”服务不特定于任何特定
  // 的远程过程调用（RPC）系统。它们由各语言的主要代码生成器生成
  // （无需额外的插件）。在 google.protobuf 的早期版本中，通用服务
  // 是唯一受支持的服务生成方式。
  //
  //
  // 现在通用服务已被视为弃用，建议改用能针对你特定的 RPC 系统
  // 生成代码的插件。因此，这些选项默认为 false。依赖通用服务的
  // 旧代码应显式将其设为 true。
  //
  optional bool cc_generic_services = 16 [default = false];
  optional bool java_generic_services = 17 [default = false];
  optional bool py_generic_services = 18 [default = false];
  optional bool php_generic_services = 42 [default = false];

  // 此文件是否弃用？
  // 视目标平台而定，可以为相应对象生成弃用（Deprecated）注解，
  // 也可能被完全忽略；至少，这是对文件弃用的一种正式声明。
  //
  optional bool deprecated = 23 [default = false];

  // 对此文件中的 proto 消息启用 arena 分配。此设置仅适用于为
  // C++ 生成的类。
  optional bool cc_enable_arenas = 31 [default = true];

  // 设置 objective c 类前缀，该前缀会加在从此 .proto 生成的所有
  // objective c 类之前。没有默认值。
  optional string objc_class_prefix = 36;

  // 生成类的命名空间；默认为包名。
  optional string csharp_namespace = 37;

  // 默认情况下，Swift 生成器会取 proto 包名并将其转换为驼峰命名
  // （camelCase，即把 '.' 替换为下划线），用它作为所定义类型/符号
  // 的前缀。如果提供了此选项，则改用此值作为所定义类型/符号的
  // 前缀。
  optional string swift_prefix = 39;

  // 设置 php 类前缀，该前缀会加在从此 .proto 生成的所有 php 类
  // 之前。默认为空。
  optional string php_class_prefix = 40;

  // 使用此选项更改 php 生成类的命名空间。默认为空。此选项为空时，
  // 将使用包名来确定命名空间。
  //
  optional string php_namespace = 41;

  // 使用此选项更改 php 生成的元数据类的命名空间。默认为空。此
  // 选项为空时，将使用 proto 文件名来确定命名空间。
  //
  optional string php_metadata_namespace = 44;

  // 使用此选项更改 ruby 生成类的包。默认为空。未设置此选项时，
  // 将使用包名来确定 ruby 包。
  //
  optional string ruby_package = 45;

  // 解析器会把它无法识别的选项存储在这里。
  // 参见上文 “Options” 一节的文档。
  repeated UninterpretedOption uninterpreted_option = 999;

  // 客户端可以在本消息的扩展中定义自定义选项。
  // 参见上文 “Options” 一节的文档。
  extensions 1000 to max;

  reserved 38;
}

message MessageOptions {
  // 设为 true 可对扩展使用旧的 proto1 MessageSet 线路格式
  // （wire format）。提供此选项是为了与 MessageSet 线路格式向后
  // 兼容。除此之外不应使用它：它效率更低、特性更少，而且更复杂。
  //
  //
  // 消息必须严格按照如下方式定义：
  //   message Foo {
  //     option message_set_wire_format = true;
  //     extensions 4 to max;
  //   }
  // 注意，该消息不能定义任何字段；MessageSet 只能有扩展。
  //
  //
  // 你的类型的所有扩展都必须是单数（singular）消息；例如它们不能
  // 是 int32、枚举或 repeated 消息。
  //
  // 由于这是一个选项，上述两条限制不会由协议编译器强制执行。
  //
  optional bool message_set_wire_format = 1 [default = false];

  // 禁用标准 `descriptor()` 访问器（accessor）的生成，该访问器可能
  // 与同名字段冲突。这是为了让从 proto1 迁移更容易；新代码应避免
  // 使用名为 "descriptor" 的字段。
  optional bool no_standard_descriptor_accessor = 2 [default = false];

  // 此消息是否弃用？
  // 视目标平台而定，可以为相应对象生成弃用（Deprecated）注解，
  // 也可能被完全忽略；至少，这是对消息弃用的一种正式声明。
  //
  optional bool deprecated = 3 [default = false];

  reserved 4, 5, 6;

  // 该消息是否是为映射字段自动生成的映射条目（map entry）类型。
  //
  //
  // 对于映射字段：
  //     map&lt;KeyType, ValueType&gt; map_field = 1;
  // 解析得到的描述符形如：
  //     message MapFieldEntry {
  //         option map_entry = true;
  //         optional KeyType key = 1;
  //         optional ValueType value = 2;
  //     }
  //     repeated MapFieldEntry map_field = 1;
  //
  // 实现可以选择不生成 map_entry=true 的消息，而是在目标语言中
  // 使用原生映射来保存键和值。此类实现中的反射 API 仍需像处理
  // repeated 消息字段那样工作。
  //
  //
  // 注意：不要在 .proto 文件中设置此选项。请始终改用映射语法。
  // 此选项只应由协议编译器的解析器隐式设置。
  //
  optional bool map_entry = 7;

  reserved 8;  // javalite_serializable
  reserved 9;  // javanano_as_lite

  // 解析器会把它无法识别的选项存储在这里。参见上文。
  repeated UninterpretedOption uninterpreted_option = 999;

  // 客户端可以在本消息的扩展中定义自定义选项。参见上文。
  extensions 1000 to max;
}

message FieldOptions {
  // ctype 选项指示 C++ 代码生成器对该字段使用与通常不同的
  // 表示。具体选项见下文。此选项在开源发布版中尚未实现——
  // 抱歉，我们会尽量在未来的版本中加入！
  //
  optional CType ctype = 1 [default = STRING];
  enum CType {
    // 默认模式。
    STRING = 0;

CORD = 1;

STRING_PIECE = 2;

  }
  // 可为 repeated 的原始类型字段启用 packed 选项，以便在线路
  // 上获得更高效的表示。无需为每个元素重复写入标签与类型，
  // 整个数组会被编码为单个长度限定（length-delimited）的
  // 数据块。在 proto3 中，只有显式将其设为 false 才会避免使用
  // 紧凑编码（packed）。
  optional bool packed = 2;

  // jstype 选项决定字段值使用的 JavaScript 类型。此选项仅适用于
  // 64 位整数与固定宽度类型（int64、uint64、sint64、fixed64、
  // sfixed64）。jstype 为 JS_STRING 的字段会表示为 JavaScript
  // 字符串，从而避免把大数值转换为 JavaScript 浮点数时可能
  // 发生的精度丢失。为 jstype 指定 JS_NUMBER 会使生成的
  // JavaScript 代码使用 JavaScript 的 "number" 类型。默认选项
  // JS_NORMAL 的行为取决于具体实现。
  //
  //
  // 此选项采用枚举形式，以便日后加入更多类型，例如
  // goog.math.Integer。
  optional JSType jstype = 6 [default = JS_NORMAL];
  enum JSType {
    // 使用默认类型。
    JS_NORMAL = 0;

// 使用 JavaScript 字符串。
JS_STRING = 1;

// 使用 JavaScript 数字。
JS_NUMBER = 2;

  }

  // 此字段是否应惰性解析？惰性仅适用于消息类型的字段。它意味着
  // 当外层消息初次解析时，内层消息的内容不会被解析，而是以编码
  // 形式存储。内层消息会在首次访问时才真正解析。
  //
  //
  // 这只是一个提示。无论此选项的取值如何，实现都可以自行选择
  // 使用立即解析还是惰性解析。不过，将此选项设为 true 表明，
  // 协议作者认为对该字段使用惰性解析是值得的，即使实现它
  // 通常需要额外的簿记开销。
  //
  //
  // 此选项不影响任何生成代码的公开接口；所有方法签名保持不变。
  // 此外，接口的线程安全性也不受此选项影响；const 方法仍然可以
  // 安全地从多个线程并发调用，而非 const 方法仍需要独占访问。
  //
  //
  //
  //
  // 注意，实现可以选择不检查惰性子消息中的 required 字段。
  // 也就是说，即使内层消息缺失 required 字段，在外层消息上
  // 调用 IsInitialized() 也可能返回 true。这是必要的，否则就
  // 必须解析内层消息才能执行检查，从而使惰性解析失去意义。
  // 选择不检查 required 字段的实现必须保持一致。也就是说，
  // 对任何一个特定的子消息，实现必须 *始终* 检查其 required
  // 字段，或者 *从不* 检查，而与该消息是否已解析无关。
  //
  //
  //
  optional bool lazy = 5 [default = false];

  // 此字段是否弃用？
  // 视目标平台而定，可以为相应对象生成弃用（Deprecated）注解，
  // 也可能被完全忽略；至少，这是对字段弃用的一种正式声明。
  //
  optional bool deprecated = 3 [default = false];

  // 仅供 Google 内部迁移使用。请勿使用。
  optional bool weak = 10 [default = false];

  // 解析器会把它无法识别的选项存储在这里。参见上文。
  repeated UninterpretedOption uninterpreted_option = 999;

  // 客户端可以在本消息的扩展中定义自定义选项。参见上文。
  extensions 1000 to max;

  reserved 4;  // 已移除的 jtype
}

message OneofOptions {
  // 解析器会把它无法识别的选项存储在这里。参见上文。
  repeated UninterpretedOption uninterpreted_option = 999;

  // 客户端可以在本消息的扩展中定义自定义选项。参见上文。
  extensions 1000 to max;
}

message EnumOptions {

  // 将此选项设为 true，即可允许把不同的枚举项名称映射到同一个
  // 值。
  optional bool allow_alias = 2;

  // 此枚举是否弃用？
  // 视目标平台而定，可以为相应对象生成弃用（Deprecated）注解，
  // 也可能被完全忽略；至少，这是对枚举弃用的一种正式声明。
  //
  optional bool deprecated = 3 [default = false];

  reserved 5;  // javanano_as_lite

  // 解析器会把它无法识别的选项存储在这里。参见上文。
  repeated UninterpretedOption uninterpreted_option = 999;

  // 客户端可以在本消息的扩展中定义自定义选项。参见上文。
  extensions 1000 to max;
}

message EnumValueOptions {
  // 此枚举值是否弃用？
  // 视目标平台而定，可以为相应对象生成弃用（Deprecated）注解，
  // 也可能被完全忽略；至少，这是对枚举值弃用的一种正式声明。
  //
  optional bool deprecated = 1 [default = false];

  // 解析器会把它无法识别的选项存储在这里。参见上文。
  repeated UninterpretedOption uninterpreted_option = 999;

  // 客户端可以在本消息的扩展中定义自定义选项。参见上文。
  extensions 1000 to max;
}

message ServiceOptions {

  // 注意：字段编号 1 到 32 保留给 Google 内部的 RPC 框架。我们
  // 把这些编号据为己有，深表歉意——早在决定发布 Protocol
  // Buffers 之前，我们就已经在使用它们了。
  //

  // 此服务是否弃用？
  // 视目标平台而定，可以为相应对象生成弃用（Deprecated）注解，
  // 也可能被完全忽略；至少，这是对服务弃用的一种正式声明。
  //
  optional bool deprecated = 33 [default = false];

  // 解析器会把它无法识别的选项存储在这里。参见上文。
  repeated UninterpretedOption uninterpreted_option = 999;

  // 客户端可以在本消息的扩展中定义自定义选项。参见上文。
  extensions 1000 to max;
}

message MethodOptions {

  // 注意：字段编号 1 到 32 保留给 Google 内部的 RPC 框架。我们
  // 把这些编号据为己有，深表歉意——早在决定发布 Protocol
  // Buffers 之前，我们就已经在使用它们了。
  //

  // 此方法是否弃用？
  // 视目标平台而定，可以为相应对象生成弃用（Deprecated）注解，
  // 也可能被完全忽略；至少，这是对方法弃用的一种正式声明。
  //
  optional bool deprecated = 33 [default = false];

  // 此方法是无副作用的（按 HTTP 术语即“安全”），还是幂等的，
  // 还是二者皆非？基于 HTTP 的 RPC 实现可以针对安全方法选用
  // GET 动词，针对幂等方法选用 PUT 动词，而非默认的 POST。
  enum IdempotencyLevel {
    IDEMPOTENCY_UNKNOWN = 0;
    NO_SIDE_EFFECTS = 1;  // 隐含幂等
    IDEMPOTENT = 2;       // 幂等，但可能有副作用
  }
  optional IdempotencyLevel idempotency_level = 34
      [default = IDEMPOTENCY_UNKNOWN];

  // 解析器会把它无法识别的选项存储在这里。参见上文。
  repeated UninterpretedOption uninterpreted_option = 999;

  // 客户端可以在本消息的扩展中定义自定义选项。参见上文。
  extensions 1000 to max;
}

// 表示解析器无法识别的选项的消息。它只出现在由
// compiler::Parser 类创建的 options proto 中。DescriptorPool 在构建
// 描述符对象时会解析这些选项。因此，描述符对象中的 options
// proto（例如由 Descriptor::options() 返回，或由
// Descriptor::CopyTo() 生成）绝不会包含 UninterpretedOption。
//
message UninterpretedOption {
  // 未解析选项的名称。每个字符串表示点分隔名称中的一段。当某一段
  // 表示扩展（在 .proto 文件的选项说明中以括号标示）时，
  // is_extension 为 true。例如，{ ["foo", false], ["bar.baz", true],
  // ["qux", false] } 表示 "foo.(bar.baz).qux"。
  //
  message NamePart {
    required string name_part = 1;
    required bool is_extension = 2;
  }
  repeated NamePart name = 2;

  // 未解析选项的值，其类型为词法分析器在解析时判定的类型。
  // 这些字段中应当恰好设置一个。
  optional string identifier_value = 3;
  optional uint64 positive_int_value = 4;
  optional int64 negative_int_value = 5;
  optional double double_value = 6;
  optional bytes string_value = 7;
  optional string aggregate_value = 8;
}

// ===================================================================
// 可选的源代码信息

// 封装关于生成 FileDescriptorProto 的原始源文件的信息。
//
message SourceCodeInfo {
  // Location 标识 .proto 文件中与某个特定定义相对应的一段源代码。
  // 这些信息旨在对 IDE、代码索引器、文档生成器以及类似工具有用。
  //
  //
  //
  // 例如，假设我们有这样一个文件：
  //   message Foo {
  //     optional string foo = 1;
  //   }
  // 只看其中这一个字段定义：
  //   optional string foo = 1;
  //   ^       ^^     ^^  ^  ^^^
  //   a       bc     de  f  ghi
  // 我们有如下位置：
  //   span（区间）  path（路径）           表示的内容
  //   [a,i)  [ 4, 0, 2, 0 ]     整个字段定义。
  //   [a,b)  [ 4, 0, 2, 0, 4 ]  标签（optional）。
  //   [c,d)  [ 4, 0, 2, 0, 5 ]  类型（string）。
  //   [e,f)  [ 4, 0, 2, 0, 1 ]  名称（foo）。
  //   [g,h)  [ 4, 0, 2, 0, 3 ]  编号（1）。
  //
  // 注意事项：
  // - 某个位置可以指向 repeated 字段本身（即不指向其中的任何
  //   特定索引）。只要一组元素在逻辑上被包含在同一段代码中，
  //   就会使用这种方式。例如，整个 extend 块（可能包含多个扩展
  //   定义）会有一个外层位置，其路径指向 "extensions" 这个
  //   repeated 字段而不带索引。
  //
  // - 多个位置可能具有相同的路径。当单个逻辑声明分散在多处时
  //   就会出现这种情况。最明显的例子还是 "extend" 块——同一
  //   作用域中可能有多个 extend 块，每个块都会有相同的路径。
  //
  // - 位置的 span 并不总是其父级 span 的子集。例如，扩展声明的
  //   "extendee" 出现在 "extend" 块的开头，并由块内所有扩展共享。
  //
  //
  // - 某个位置的 span 是另一个位置 span 的子集，并不意味着它是
  //   后者的后代。例如，“组（group）” 在单个声明中同时定义了
  //   一个类型和一个字段。因此，与该类型和字段及其组成部分对应
  //   的位置会相互重叠。
  // - 尝试解读位置的代码最好设计成忽略它不理解的位置，因为
  //   未来可能会记录更多类型的位置。
  //
  repeated Location location = 1;
  message Location {
    // 标识 FileDescriptorProto 的哪个部分定义于此位置。
    //
    //
    // 每个元素要么是字段编号，要么是索引。它们构成从根
    // FileDescriptorProto 到定义所在位置的路径。例如，路径：
    //
    //   [ 4, 3, 2, 7, 1 ]
    // 指向：
    //   file.message_type(3)  // 4, 3
    //       .field(7)         // 2, 7
    //       .name()           // 1
    // 这是因为 FileDescriptorProto.message_type 的字段编号为 4：
    //   repeated DescriptorProto message_type = 4;
    // 而 DescriptorProto.field 的字段编号为 2：
    //   repeated FieldDescriptorProto field = 2;
    // 且 FieldDescriptorProto.name 的字段编号为 1：
    //   optional string name = 1;
    //
    // 因此，上述路径给出了一个字段名的位置。如果去掉最后一个
    // 元素：
    //   [ 4, 3, 2, 7 ]
    // 该路径指向整个字段声明（从标签开头到结尾的分号）。
    //
    repeated int32 path = 1 [packed = true];

// 始终恰有三个或四个元素：起始行、起始列、结束行（可选，
// 缺省时假定与起始行相同）、结束列。
// 为提高效率，它们被紧凑打包在单个字段中。注意，行号与列号
// 从零开始计数——通常在展示给用户之前，你需要给每个值加 1。
//
repeated int32 span = 2 [packed = true];

// 如果此 SourceCodeInfo 表示一个完整的声明，则这些字段是该声明
// 前后出现、看起来附着于该声明的注释。
//
//
// 出现在连续行上、且这些行上没有其他记号的一系列行注释，
// 会被视为单条注释。
//
// leading_detached_comments 会保存在当前元素之前出现（但并未
// 与当前元素相连）的注释段落。每个段落以空行分隔，将成为
// repeated 字段中的一个注释元素。
//
//
// 只提供注释内容；注释标记（例如 //）会被去除。对于块注释，
// 除第一行外，每行开头的空白与星号都会被去除。换行符会
// 保留在输出中。
//
//
// 示例：
//
//   optional int32 foo = 1;  // 附着于 foo 的注释。
//   // 附着于 bar 的注释。
//   optional int32 bar = 2;
//
//   optional string baz = 3;
//   // 附着于 baz 的注释。
//   // 附着于 baz 的另一行注释。
//
//   // 附着于 qux 的注释。
//   //
//   // 附着于 qux 的另一行注释。
//   optional double qux = 4;
//
//   // corge 的分离注释。它既不是 qux 也不是 corge 的前导或
//   // 尾随注释，因为它与两者之间都有空行分隔。
//
//
//   // corge 的分离注释第二段。
//
//   optional string corge = 5;
//   /* 附着于 corge 的
//    * 块注释。前导的星号
//    * 将被移除。 */ // /* 附着于
//    * grault 的块注释。 */
//   optional int32 grault = 6;
//
//   // 被忽略的分离注释。
optional string leading_comments = 3;
optional string trailing_comments = 4;
repeated string leading_detached_comments = 6;

  }
}

// 描述生成代码与其原始源文件之间的关系。一个 GeneratedCodeInfo
// 消息只与一个生成的源文件关联，但可以包含对多个不同源
// .proto 文件的引用。
message GeneratedCodeInfo {
  // Annotation 把生成代码中的某段文本与生成它的 .proto 文件中的
  // 某个元素关联起来。
  repeated Annotation annotation = 1;
  message Annotation {
    // 标识原始源 .proto 文件中的元素。此字段的格式与
    // SourceCodeInfo.Location.path 相同。
    repeated int32 path = 1 [packed = true];

// 标识原始源 .proto 文件的文件系统路径。
optional string source_file = 2;

// 标识生成代码中与所标识对象相关的起始字节偏移量。
//
optional int32 begin = 3;

// 标识生成代码中与所标识对象相关的结束字节偏移量。结束偏移量
// 应为最后一个相关字节之后的位置（即文本长度 = end - begin）。
//
optional int32 end = 4;

  }
}
</pre><table width="100%"><tr><th colspan="2"><h3 style="margin-top: 4px">本文件中的类</h3></th></tr></table><table><tr><th colspan="2"><h3 style="margin-top: 4px">文件成员</h3><div style="font-style: italic; font-weight: normal;">这些定义不属于任何类。</div></th></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>enum</code></td><td style="border-left-width: 0px"id="FieldDescriptorProto_Type"><div style="padding-left: 16px; text-indent: -16px"><code><b>FieldDescriptorProto_Type</b></code></div><div style="font-style: italic; margin-top: 4px; margin-left: 16px;"> <a href="#FieldDescriptorProto_Type.details">更多……</a></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>enum</code></td><td style="border-left-width: 0px"id="FieldDescriptorProto_Label"><div style="padding-left: 16px; text-indent: -16px"><code><b>FieldDescriptorProto_Label</b></code></div><div style="font-style: italic; margin-top: 4px; margin-left: 16px;"> <a href="#FieldDescriptorProto_Label.details">更多……</a></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>enum</code></td><td style="border-left-width: 0px"id="FileOptions_OptimizeMode"><div style="padding-left: 16px; text-indent: -16px"><code><b>FileOptions_OptimizeMode</b></code></div><div style="font-style: italic; margin-top: 4px; margin-left: 16px;"> <a href="#FileOptions_OptimizeMode.details">更多……</a></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>enum</code></td><td style="border-left-width: 0px"id="FieldOptions_CType"><div style="padding-left: 16px; text-indent: -16px"><code><b>FieldOptions_CType</b></code></div><div style="font-style: italic; margin-top: 4px; margin-left: 16px;"> <a href="#FieldOptions_CType.details">更多……</a></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>enum</code></td><td style="border-left-width: 0px"id="FieldOptions_JSType"><div style="padding-left: 16px; text-indent: -16px"><code><b>FieldOptions_JSType</b></code></div><div style="font-style: italic; margin-top: 4px; margin-left: 16px;"> <a href="#FieldOptions_JSType.details">更多……</a></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>enum</code></td><td style="border-left-width: 0px"id="MethodOptions_IdempotencyLevel"><div style="padding-left: 16px; text-indent: -16px"><code><b>MethodOptions_IdempotencyLevel</b></code></div><div style="font-style: italic; margin-top: 4px; margin-left: 16px;"> <a href="#MethodOptions_IdempotencyLevel.details">更多……</a></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>const ::protobuf::internal::DescriptorTable</code></td><td style="border-left-width: 0px"id="descriptor_table_google_2fprotobuf_2fdescriptor_2eproto"><div style="padding-left: 16px; text-indent: -16px"><code><b>descriptor_table_google_2fprotobuf_2fdescriptor_2eproto</b></code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>DescriptorProtoDefaultTypeInternal</code></td><td style="border-left-width: 0px"id="_DescriptorProto_default_instance_"><div style="padding-left: 16px; text-indent: -16px"><code><b>_DescriptorProto_default_instance_</b></code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>DescriptorProto_ExtensionRangeDefaultTypeInternal</code></td><td style="border-left-width: 0px"id="_DescriptorProto_ExtensionRange_default_instance_"><div style="padding-left: 16px; text-indent: -16px"><code><b>_DescriptorProto_ExtensionRange_default_instance_</b></code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>DescriptorProto_ReservedRangeDefaultTypeInternal</code></td><td style="border-left-width: 0px"id="_DescriptorProto_ReservedRange_default_instance_"><div style="padding-left: 16px; text-indent: -16px"><code><b>_DescriptorProto_ReservedRange_default_instance_</b></code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>EnumDescriptorProtoDefaultTypeInternal</code></td><td style="border-left-width: 0px"id="_EnumDescriptorProto_default_instance_"><div style="padding-left: 16px; text-indent: -16px"><code><b>_EnumDescriptorProto_default_instance_</b></code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>EnumDescriptorProto_EnumReservedRangeDefaultTypeInternal</code></td><td style="border-left-width: 0px"id="_EnumDescriptorProto_EnumReservedRange_default_instance_"><div style="padding-left: 16px; text-indent: -16px"><code><b>_EnumDescriptorProto_EnumReservedRange_default_instance_</b></code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>EnumOptionsDefaultTypeInternal</code></td><td style="border-left-width: 0px"id="_EnumOptions_default_instance_"><div style="padding-left: 16px; text-indent: -16px"><code><b>_EnumOptions_default_instance_</b></code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>EnumValueDescriptorProtoDefaultTypeInternal</code></td><td style="border-left-width: 0px"id="_EnumValueDescriptorProto_default_instance_"><div style="padding-left: 16px; text-indent: -16px"><code><b>_EnumValueDescriptorProto_default_instance_</b></code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>EnumValueOptionsDefaultTypeInternal</code></td><td style="border-left-width: 0px"id="_EnumValueOptions_default_instance_"><div style="padding-left: 16px; text-indent: -16px"><code><b>_EnumValueOptions_default_instance_</b></code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>ExtensionRangeOptionsDefaultTypeInternal</code></td><td style="border-left-width: 0px"id="_ExtensionRangeOptions_default_instance_"><div style="padding-left: 16px; text-indent: -16px"><code><b>_ExtensionRangeOptions_default_instance_</b></code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>FieldDescriptorProtoDefaultTypeInternal</code></td><td style="border-left-width: 0px"id="_FieldDescriptorProto_default_instance_"><div style="padding-left: 16px; text-indent: -16px"><code><b>_FieldDescriptorProto_default_instance_</b></code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>FieldOptionsDefaultTypeInternal</code></td><td style="border-left-width: 0px"id="_FieldOptions_default_instance_"><div style="padding-left: 16px; text-indent: -16px"><code><b>_FieldOptions_default_instance_</b></code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>FileDescriptorProtoDefaultTypeInternal</code></td><td style="border-left-width: 0px"id="_FileDescriptorProto_default_instance_"><div style="padding-left: 16px; text-indent: -16px"><code><b>_FileDescriptorProto_default_instance_</b></code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>FileDescriptorSetDefaultTypeInternal</code></td><td style="border-left-width: 0px"id="_FileDescriptorSet_default_instance_"><div style="padding-left: 16px; text-indent: -16px"><code><b>_FileDescriptorSet_default_instance_</b></code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>FileOptionsDefaultTypeInternal</code></td><td style="border-left-width: 0px"id="_FileOptions_default_instance_"><div style="padding-left: 16px; text-indent: -16px"><code><b>_FileOptions_default_instance_</b></code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>GeneratedCodeInfoDefaultTypeInternal</code></td><td style="border-left-width: 0px"id="_GeneratedCodeInfo_default_instance_"><div style="padding-left: 16px; text-indent: -16px"><code><b>_GeneratedCodeInfo_default_instance_</b></code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>GeneratedCodeInfo_AnnotationDefaultTypeInternal</code></td><td style="border-left-width: 0px"id="_GeneratedCodeInfo_Annotation_default_instance_"><div style="padding-left: 16px; text-indent: -16px"><code><b>_GeneratedCodeInfo_Annotation_default_instance_</b></code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>MessageOptionsDefaultTypeInternal</code></td><td style="border-left-width: 0px"id="_MessageOptions_default_instance_"><div style="padding-left: 16px; text-indent: -16px"><code><b>_MessageOptions_default_instance_</b></code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>MethodDescriptorProtoDefaultTypeInternal</code></td><td style="border-left-width: 0px"id="_MethodDescriptorProto_default_instance_"><div style="padding-left: 16px; text-indent: -16px"><code><b>_MethodDescriptorProto_default_instance_</b></code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>MethodOptionsDefaultTypeInternal</code></td><td style="border-left-width: 0px"id="_MethodOptions_default_instance_"><div style="padding-left: 16px; text-indent: -16px"><code><b>_MethodOptions_default_instance_</b></code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>OneofDescriptorProtoDefaultTypeInternal</code></td><td style="border-left-width: 0px"id="_OneofDescriptorProto_default_instance_"><div style="padding-left: 16px; text-indent: -16px"><code><b>_OneofDescriptorProto_default_instance_</b></code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>OneofOptionsDefaultTypeInternal</code></td><td style="border-left-width: 0px"id="_OneofOptions_default_instance_"><div style="padding-left: 16px; text-indent: -16px"><code><b>_OneofOptions_default_instance_</b></code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>ServiceDescriptorProtoDefaultTypeInternal</code></td><td style="border-left-width: 0px"id="_ServiceDescriptorProto_default_instance_"><div style="padding-left: 16px; text-indent: -16px"><code><b>_ServiceDescriptorProto_default_instance_</b></code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>ServiceOptionsDefaultTypeInternal</code></td><td style="border-left-width: 0px"id="_ServiceOptions_default_instance_"><div style="padding-left: 16px; text-indent: -16px"><code><b>_ServiceOptions_default_instance_</b></code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>SourceCodeInfoDefaultTypeInternal</code></td><td style="border-left-width: 0px"id="_SourceCodeInfo_default_instance_"><div style="padding-left: 16px; text-indent: -16px"><code><b>_SourceCodeInfo_default_instance_</b></code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>SourceCodeInfo_LocationDefaultTypeInternal</code></td><td style="border-left-width: 0px"id="_SourceCodeInfo_Location_default_instance_"><div style="padding-left: 16px; text-indent: -16px"><code><b>_SourceCodeInfo_Location_default_instance_</b></code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>UninterpretedOptionDefaultTypeInternal</code></td><td style="border-left-width: 0px"id="_UninterpretedOption_default_instance_"><div style="padding-left: 16px; text-indent: -16px"><code><b>_UninterpretedOption_default_instance_</b></code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>UninterpretedOption_NamePartDefaultTypeInternal</code></td><td style="border-left-width: 0px"id="_UninterpretedOption_NamePart_default_instance_"><div style="padding-left: 16px; text-indent: -16px"><code><b>_UninterpretedOption_NamePart_default_instance_</b></code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>constexpr FieldDescriptorProto_Type</code></td><td style="border-left-width: 0px"id="FieldDescriptorProto_Type_Type_MIN"><div style="padding-left: 16px; text-indent: -16px"><code><b>FieldDescriptorProto_Type_Type_MIN</b> = = FieldDescriptorProto_Type_TYPE_DOUBLE</code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>constexpr FieldDescriptorProto_Type</code></td><td style="border-left-width: 0px"id="FieldDescriptorProto_Type_Type_MAX"><div style="padding-left: 16px; text-indent: -16px"><code><b>FieldDescriptorProto_Type_Type_MAX</b> = = FieldDescriptorProto_Type_TYPE_SINT64</code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>constexpr int</code></td><td style="border-left-width: 0px"id="FieldDescriptorProto_Type_Type_ARRAYSIZE"><div style="padding-left: 16px; text-indent: -16px"><code><b>FieldDescriptorProto_Type_Type_ARRAYSIZE</b> = = FieldDescriptorProto_Type_Type_MAX + 1</code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>constexpr FieldDescriptorProto_Label</code></td><td style="border-left-width: 0px"id="FieldDescriptorProto_Label_Label_MIN"><div style="padding-left: 16px; text-indent: -16px"><code><b>FieldDescriptorProto_Label_Label_MIN</b> = = FieldDescriptorProto_Label_LABEL_OPTIONAL</code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>constexpr FieldDescriptorProto_Label</code></td><td style="border-left-width: 0px"id="FieldDescriptorProto_Label_Label_MAX"><div style="padding-left: 16px; text-indent: -16px"><code><b>FieldDescriptorProto_Label_Label_MAX</b> = = FieldDescriptorProto_Label_LABEL_REPEATED</code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>constexpr int</code></td><td style="border-left-width: 0px"id="FieldDescriptorProto_Label_Label_ARRAYSIZE"><div style="padding-left: 16px; text-indent: -16px"><code><b>FieldDescriptorProto_Label_Label_ARRAYSIZE</b> = = FieldDescriptorProto_Label_Label_MAX + 1</code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>constexpr FileOptions_OptimizeMode</code></td><td style="border-left-width: 0px"id="FileOptions_OptimizeMode_OptimizeMode_MIN"><div style="padding-left: 16px; text-indent: -16px"><code><b>FileOptions_OptimizeMode_OptimizeMode_MIN</b> = = FileOptions_OptimizeMode_SPEED</code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>constexpr FileOptions_OptimizeMode</code></td><td style="border-left-width: 0px"id="FileOptions_OptimizeMode_OptimizeMode_MAX"><div style="padding-left: 16px; text-indent: -16px"><code><b>FileOptions_OptimizeMode_OptimizeMode_MAX</b> = = FileOptions_OptimizeMode_LITE_RUNTIME</code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>constexpr int</code></td><td style="border-left-width: 0px"id="FileOptions_OptimizeMode_OptimizeMode_ARRAYSIZE"><div style="padding-left: 16px; text-indent: -16px"><code><b>FileOptions_OptimizeMode_OptimizeMode_ARRAYSIZE</b> = = FileOptions_OptimizeMode_OptimizeMode_MAX + 1</code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>constexpr FieldOptions_CType</code></td><td style="border-left-width: 0px"id="FieldOptions_CType_CType_MIN"><div style="padding-left: 16px; text-indent: -16px"><code><b>FieldOptions_CType_CType_MIN</b> = = FieldOptions_CType_STRING</code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>constexpr FieldOptions_CType</code></td><td style="border-left-width: 0px"id="FieldOptions_CType_CType_MAX"><div style="padding-left: 16px; text-indent: -16px"><code><b>FieldOptions_CType_CType_MAX</b> = = FieldOptions_CType_STRING_PIECE</code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>constexpr int</code></td><td style="border-left-width: 0px"id="FieldOptions_CType_CType_ARRAYSIZE"><div style="padding-left: 16px; text-indent: -16px"><code><b>FieldOptions_CType_CType_ARRAYSIZE</b> = = FieldOptions_CType_CType_MAX + 1</code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>constexpr FieldOptions_JSType</code></td><td style="border-left-width: 0px"id="FieldOptions_JSType_JSType_MIN"><div style="padding-left: 16px; text-indent: -16px"><code><b>FieldOptions_JSType_JSType_MIN</b> = = FieldOptions_JSType_JS_NORMAL</code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>constexpr FieldOptions_JSType</code></td><td style="border-left-width: 0px"id="FieldOptions_JSType_JSType_MAX"><div style="padding-left: 16px; text-indent: -16px"><code><b>FieldOptions_JSType_JSType_MAX</b> = = FieldOptions_JSType_JS_NUMBER</code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>constexpr int</code></td><td style="border-left-width: 0px"id="FieldOptions_JSType_JSType_ARRAYSIZE"><div style="padding-left: 16px; text-indent: -16px"><code><b>FieldOptions_JSType_JSType_ARRAYSIZE</b> = = FieldOptions_JSType_JSType_MAX + 1</code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>constexpr MethodOptions_IdempotencyLevel</code></td><td style="border-left-width: 0px"id="MethodOptions_IdempotencyLevel_IdempotencyLevel_MIN"><div style="padding-left: 16px; text-indent: -16px"><code><b>MethodOptions_IdempotencyLevel_IdempotencyLevel_MIN</b> = = MethodOptions_IdempotencyLevel_IDEMPOTENCY_UNKNOWN</code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>constexpr MethodOptions_IdempotencyLevel</code></td><td style="border-left-width: 0px"id="MethodOptions_IdempotencyLevel_IdempotencyLevel_MAX"><div style="padding-left: 16px; text-indent: -16px"><code><b>MethodOptions_IdempotencyLevel_IdempotencyLevel_MAX</b> = = MethodOptions_IdempotencyLevel_IDEMPOTENT</code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>constexpr int</code></td><td style="border-left-width: 0px"id="MethodOptions_IdempotencyLevel_IdempotencyLevel_ARRAYSIZE"><div style="padding-left: 16px; text-indent: -16px"><code><b>MethodOptions_IdempotencyLevel_IdempotencyLevel_ARRAYSIZE</b> = = MethodOptions_IdempotencyLevel_IdempotencyLevel_MAX + 1</code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>PROTOBUF_NAMESPACE_CLOSE PROTOBUF_NAMESPACE_OPEN protobuf::DescriptorProto *</code></td><td style="border-left-width: 0px"id="Arena::CreateMaybeMessage< protobuf::DescriptorProto >"><div style="padding-left: 16px; text-indent: -16px"><code><b>Arena::CreateMaybeMessage< protobuf::DescriptorProto ></b>(Arena * )</code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>protobuf::DescriptorProto_ExtensionRange *</code></td><td style="border-left-width: 0px"id="Arena::CreateMaybeMessage< protobuf::DescriptorProto_ExtensionRange >"><div style="padding-left: 16px; text-indent: -16px"><code><b>Arena::CreateMaybeMessage< protobuf::DescriptorProto_ExtensionRange ></b>(Arena * )</code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>protobuf::DescriptorProto_ReservedRange *</code></td><td style="border-left-width: 0px"id="Arena::CreateMaybeMessage< protobuf::DescriptorProto_ReservedRange >"><div style="padding-left: 16px; text-indent: -16px"><code><b>Arena::CreateMaybeMessage< protobuf::DescriptorProto_ReservedRange ></b>(Arena * )</code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>protobuf::EnumDescriptorProto *</code></td><td style="border-left-width: 0px"id="Arena::CreateMaybeMessage< protobuf::EnumDescriptorProto >"><div style="padding-left: 16px; text-indent: -16px"><code><b>Arena::CreateMaybeMessage< protobuf::EnumDescriptorProto ></b>(Arena * )</code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>protobuf::EnumDescriptorProto_EnumReservedRange *</code></td><td style="border-left-width: 0px"id="Arena::CreateMaybeMessage< protobuf::EnumDescriptorProto_EnumReservedRange >"><div style="padding-left: 16px; text-indent: -16px"><code><b>Arena::CreateMaybeMessage< protobuf::EnumDescriptorProto_EnumReservedRange ></b>(Arena * )</code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>protobuf::EnumOptions *</code></td><td style="border-left-width: 0px"id="Arena::CreateMaybeMessage< protobuf::EnumOptions >"><div style="padding-left: 16px; text-indent: -16px"><code><b>Arena::CreateMaybeMessage< protobuf::EnumOptions ></b>(Arena * )</code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>protobuf::EnumValueDescriptorProto *</code></td><td style="border-left-width: 0px"id="Arena::CreateMaybeMessage< protobuf::EnumValueDescriptorProto >"><div style="padding-left: 16px; text-indent: -16px"><code><b>Arena::CreateMaybeMessage< protobuf::EnumValueDescriptorProto ></b>(Arena * )</code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>protobuf::EnumValueOptions *</code></td><td style="border-left-width: 0px"id="Arena::CreateMaybeMessage< protobuf::EnumValueOptions >"><div style="padding-left: 16px; text-indent: -16px"><code><b>Arena::CreateMaybeMessage< protobuf::EnumValueOptions ></b>(Arena * )</code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>protobuf::ExtensionRangeOptions *</code></td><td style="border-left-width: 0px"id="Arena::CreateMaybeMessage< protobuf::ExtensionRangeOptions >"><div style="padding-left: 16px; text-indent: -16px"><code><b>Arena::CreateMaybeMessage< protobuf::ExtensionRangeOptions ></b>(Arena * )</code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>protobuf::FieldDescriptorProto *</code></td><td style="border-left-width: 0px"id="Arena::CreateMaybeMessage< protobuf::FieldDescriptorProto >"><div style="padding-left: 16px; text-indent: -16px"><code><b>Arena::CreateMaybeMessage< protobuf::FieldDescriptorProto ></b>(Arena * )</code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>protobuf::FieldOptions *</code></td><td style="border-left-width: 0px"id="Arena::CreateMaybeMessage< protobuf::FieldOptions >"><div style="padding-left: 16px; text-indent: -16px"><code><b>Arena::CreateMaybeMessage< protobuf::FieldOptions ></b>(Arena * )</code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>protobuf::FileDescriptorProto *</code></td><td style="border-left-width: 0px"id="Arena::CreateMaybeMessage< protobuf::FileDescriptorProto >"><div style="padding-left: 16px; text-indent: -16px"><code><b>Arena::CreateMaybeMessage< protobuf::FileDescriptorProto ></b>(Arena * )</code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>protobuf::FileDescriptorSet *</code></td><td style="border-left-width: 0px"id="Arena::CreateMaybeMessage< protobuf::FileDescriptorSet >"><div style="padding-left: 16px; text-indent: -16px"><code><b>Arena::CreateMaybeMessage< protobuf::FileDescriptorSet ></b>(Arena * )</code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>protobuf::FileOptions *</code></td><td style="border-left-width: 0px"id="Arena::CreateMaybeMessage< protobuf::FileOptions >"><div style="padding-left: 16px; text-indent: -16px"><code><b>Arena::CreateMaybeMessage< protobuf::FileOptions ></b>(Arena * )</code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>protobuf::GeneratedCodeInfo *</code></td><td style="border-left-width: 0px"id="Arena::CreateMaybeMessage< protobuf::GeneratedCodeInfo >"><div style="padding-left: 16px; text-indent: -16px"><code><b>Arena::CreateMaybeMessage< protobuf::GeneratedCodeInfo ></b>(Arena * )</code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>protobuf::GeneratedCodeInfo_Annotation *</code></td><td style="border-left-width: 0px"id="Arena::CreateMaybeMessage< protobuf::GeneratedCodeInfo_Annotation >"><div style="padding-left: 16px; text-indent: -16px"><code><b>Arena::CreateMaybeMessage< protobuf::GeneratedCodeInfo_Annotation ></b>(Arena * )</code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>protobuf::MessageOptions *</code></td><td style="border-left-width: 0px"id="Arena::CreateMaybeMessage< protobuf::MessageOptions >"><div style="padding-left: 16px; text-indent: -16px"><code><b>Arena::CreateMaybeMessage< protobuf::MessageOptions ></b>(Arena * )</code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>protobuf::MethodDescriptorProto *</code></td><td style="border-left-width: 0px"id="Arena::CreateMaybeMessage< protobuf::MethodDescriptorProto >"><div style="padding-left: 16px; text-indent: -16px"><code><b>Arena::CreateMaybeMessage< protobuf::MethodDescriptorProto ></b>(Arena * )</code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>protobuf::MethodOptions *</code></td><td style="border-left-width: 0px"id="Arena::CreateMaybeMessage< protobuf::MethodOptions >"><div style="padding-left: 16px; text-indent: -16px"><code><b>Arena::CreateMaybeMessage< protobuf::MethodOptions ></b>(Arena * )</code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>protobuf::OneofDescriptorProto *</code></td><td style="border-left-width: 0px"id="Arena::CreateMaybeMessage< protobuf::OneofDescriptorProto >"><div style="padding-left: 16px; text-indent: -16px"><code><b>Arena::CreateMaybeMessage< protobuf::OneofDescriptorProto ></b>(Arena * )</code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>protobuf::OneofOptions *</code></td><td style="border-left-width: 0px"id="Arena::CreateMaybeMessage< protobuf::OneofOptions >"><div style="padding-left: 16px; text-indent: -16px"><code><b>Arena::CreateMaybeMessage< protobuf::OneofOptions ></b>(Arena * )</code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>protobuf::ServiceDescriptorProto *</code></td><td style="border-left-width: 0px"id="Arena::CreateMaybeMessage< protobuf::ServiceDescriptorProto >"><div style="padding-left: 16px; text-indent: -16px"><code><b>Arena::CreateMaybeMessage< protobuf::ServiceDescriptorProto ></b>(Arena * )</code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>protobuf::ServiceOptions *</code></td><td style="border-left-width: 0px"id="Arena::CreateMaybeMessage< protobuf::ServiceOptions >"><div style="padding-left: 16px; text-indent: -16px"><code><b>Arena::CreateMaybeMessage< protobuf::ServiceOptions ></b>(Arena * )</code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>protobuf::SourceCodeInfo *</code></td><td style="border-left-width: 0px"id="Arena::CreateMaybeMessage< protobuf::SourceCodeInfo >"><div style="padding-left: 16px; text-indent: -16px"><code><b>Arena::CreateMaybeMessage< protobuf::SourceCodeInfo ></b>(Arena * )</code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>protobuf::SourceCodeInfo_Location *</code></td><td style="border-left-width: 0px"id="Arena::CreateMaybeMessage< protobuf::SourceCodeInfo_Location >"><div style="padding-left: 16px; text-indent: -16px"><code><b>Arena::CreateMaybeMessage< protobuf::SourceCodeInfo_Location ></b>(Arena * )</code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>protobuf::UninterpretedOption *</code></td><td style="border-left-width: 0px"id="Arena::CreateMaybeMessage< protobuf::UninterpretedOption >"><div style="padding-left: 16px; text-indent: -16px"><code><b>Arena::CreateMaybeMessage< protobuf::UninterpretedOption ></b>(Arena * )</code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>protobuf::UninterpretedOption_NamePart *</code></td><td style="border-left-width: 0px"id="Arena::CreateMaybeMessage< protobuf::UninterpretedOption_NamePart >"><div style="padding-left: 16px; text-indent: -16px"><code><b>Arena::CreateMaybeMessage< protobuf::UninterpretedOption_NamePart ></b>(Arena * )</code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>bool</code></td><td style="border-left-width: 0px"id="FieldDescriptorProto_Type_IsValid"><div style="padding-left: 16px; text-indent: -16px"><code><b>FieldDescriptorProto_Type_IsValid</b>(int value)</code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>const ::protobuf::EnumDescriptor *</code></td><td style="border-left-width: 0px"id="FieldDescriptorProto_Type_descriptor"><div style="padding-left: 16px; text-indent: -16px"><code><b>FieldDescriptorProto_Type_descriptor</b>()</code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>template const std::string &amp;</code></td><td style="border-left-width: 0px"id="FieldDescriptorProto_Type_Name"><div style="padding-left: 16px; text-indent: -16px"><code><b>FieldDescriptorProto_Type_Name</b>(T enum_t_value)</code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>bool</code></td><td style="border-left-width: 0px"id="FieldDescriptorProto_Type_Parse"><div style="padding-left: 16px; text-indent: -16px"><code><b>FieldDescriptorProto_Type_Parse</b>(::protobuf::ConstStringParam name, FieldDescriptorProto_Type * value)</code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>bool</code></td><td style="border-left-width: 0px"id="FieldDescriptorProto_Label_IsValid"><div style="padding-left: 16px; text-indent: -16px"><code><b>FieldDescriptorProto_Label_IsValid</b>(int value)</code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>const ::protobuf::EnumDescriptor *</code></td><td style="border-left-width: 0px"id="FieldDescriptorProto_Label_descriptor"><div style="padding-left: 16px; text-indent: -16px"><code><b>FieldDescriptorProto_Label_descriptor</b>()</code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>template const std::string &amp;</code></td><td style="border-left-width: 0px"id="FieldDescriptorProto_Label_Name"><div style="padding-left: 16px; text-indent: -16px"><code><b>FieldDescriptorProto_Label_Name</b>(T enum_t_value)</code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>bool</code></td><td style="border-left-width: 0px"id="FieldDescriptorProto_Label_Parse"><div style="padding-left: 16px; text-indent: -16px"><code><b>FieldDescriptorProto_Label_Parse</b>(::protobuf::ConstStringParam name, FieldDescriptorProto_Label * value)</code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>bool</code></td><td style="border-left-width: 0px"id="FileOptions_OptimizeMode_IsValid"><div style="padding-left: 16px; text-indent: -16px"><code><b>FileOptions_OptimizeMode_IsValid</b>(int value)</code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>const ::protobuf::EnumDescriptor *</code></td><td style="border-left-width: 0px"id="FileOptions_OptimizeMode_descriptor"><div style="padding-left: 16px; text-indent: -16px"><code><b>FileOptions_OptimizeMode_descriptor</b>()</code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>template const std::string &amp;</code></td><td style="border-left-width: 0px"id="FileOptions_OptimizeMode_Name"><div style="padding-left: 16px; text-indent: -16px"><code><b>FileOptions_OptimizeMode_Name</b>(T enum_t_value)</code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>bool</code></td><td style="border-left-width: 0px"id="FileOptions_OptimizeMode_Parse"><div style="padding-left: 16px; text-indent: -16px"><code><b>FileOptions_OptimizeMode_Parse</b>(::protobuf::ConstStringParam name, FileOptions_OptimizeMode * value)</code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>bool</code></td><td style="border-left-width: 0px"id="FieldOptions_CType_IsValid"><div style="padding-left: 16px; text-indent: -16px"><code><b>FieldOptions_CType_IsValid</b>(int value)</code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>const ::protobuf::EnumDescriptor *</code></td><td style="border-left-width: 0px"id="FieldOptions_CType_descriptor"><div style="padding-left: 16px; text-indent: -16px"><code><b>FieldOptions_CType_descriptor</b>()</code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>template const std::string &amp;</code></td><td style="border-left-width: 0px"id="FieldOptions_CType_Name"><div style="padding-left: 16px; text-indent: -16px"><code><b>FieldOptions_CType_Name</b>(T enum_t_value)</code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>bool</code></td><td style="border-left-width: 0px"id="FieldOptions_CType_Parse"><div style="padding-left: 16px; text-indent: -16px"><code><b>FieldOptions_CType_Parse</b>(::protobuf::ConstStringParam name, FieldOptions_CType * value)</code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>bool</code></td><td style="border-left-width: 0px"id="FieldOptions_JSType_IsValid"><div style="padding-left: 16px; text-indent: -16px"><code><b>FieldOptions_JSType_IsValid</b>(int value)</code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>const ::protobuf::EnumDescriptor *</code></td><td style="border-left-width: 0px"id="FieldOptions_JSType_descriptor"><div style="padding-left: 16px; text-indent: -16px"><code><b>FieldOptions_JSType_descriptor</b>()</code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>template const std::string &amp;</code></td><td style="border-left-width: 0px"id="FieldOptions_JSType_Name"><div style="padding-left: 16px; text-indent: -16px"><code><b>FieldOptions_JSType_Name</b>(T enum_t_value)</code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>bool</code></td><td style="border-left-width: 0px"id="FieldOptions_JSType_Parse"><div style="padding-left: 16px; text-indent: -16px"><code><b>FieldOptions_JSType_Parse</b>(::protobuf::ConstStringParam name, FieldOptions_JSType * value)</code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>bool</code></td><td style="border-left-width: 0px"id="MethodOptions_IdempotencyLevel_IsValid"><div style="padding-left: 16px; text-indent: -16px"><code><b>MethodOptions_IdempotencyLevel_IsValid</b>(int value)</code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>const ::protobuf::EnumDescriptor *</code></td><td style="border-left-width: 0px"id="MethodOptions_IdempotencyLevel_descriptor"><div style="padding-left: 16px; text-indent: -16px"><code><b>MethodOptions_IdempotencyLevel_descriptor</b>()</code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>template const std::string &amp;</code></td><td style="border-left-width: 0px"id="MethodOptions_IdempotencyLevel_Name"><div style="padding-left: 16px; text-indent: -16px"><code><b>MethodOptions_IdempotencyLevel_Name</b>(T enum_t_value)</code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>bool</code></td><td style="border-left-width: 0px"id="MethodOptions_IdempotencyLevel_Parse"><div style="padding-left: 16px; text-indent: -16px"><code><b>MethodOptions_IdempotencyLevel_Parse</b>(::protobuf::ConstStringParam name, MethodOptions_IdempotencyLevel * value)</code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>const EnumDescriptor *</code></td><td style="border-left-width: 0px"id="GetEnumDescriptor< protobuf::FieldDescriptorProto_Type >"><div style="padding-left: 16px; text-indent: -16px"><code><b>GetEnumDescriptor< protobuf::FieldDescriptorProto_Type ></b>()</code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>const EnumDescriptor *</code></td><td style="border-left-width: 0px"id="GetEnumDescriptor< protobuf::FieldDescriptorProto_Label >"><div style="padding-left: 16px; text-indent: -16px"><code><b>GetEnumDescriptor< protobuf::FieldDescriptorProto_Label ></b>()</code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>const EnumDescriptor *</code></td><td style="border-left-width: 0px"id="GetEnumDescriptor< protobuf::FileOptions_OptimizeMode >"><div style="padding-left: 16px; text-indent: -16px"><code><b>GetEnumDescriptor< protobuf::FileOptions_OptimizeMode ></b>()</code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>const EnumDescriptor *</code></td><td style="border-left-width: 0px"id="GetEnumDescriptor< protobuf::FieldOptions_CType >"><div style="padding-left: 16px; text-indent: -16px"><code><b>GetEnumDescriptor< protobuf::FieldOptions_CType ></b>()</code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>const EnumDescriptor *</code></td><td style="border-left-width: 0px"id="GetEnumDescriptor< protobuf::FieldOptions_JSType >"><div style="padding-left: 16px; text-indent: -16px"><code><b>GetEnumDescriptor< protobuf::FieldOptions_JSType ></b>()</code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>const EnumDescriptor *</code></td><td style="border-left-width: 0px"id="GetEnumDescriptor< protobuf::MethodOptions_IdempotencyLevel >"><div style="padding-left: 16px; text-indent: -16px"><code><b>GetEnumDescriptor< protobuf::MethodOptions_IdempotencyLevel ></b>()</code></div></td></tr></table> <hr><h3 id="FieldDescriptorProto_Type.details"><code>enum protobuf::FieldDescriptorProto_Type {<br>&nbsp;&nbsp;FieldDescriptorProto_Type_TYPE_DOUBLE = = 1,<br>&nbsp;&nbsp;FieldDescriptorProto_Type_TYPE_FLOAT = = 2,<br>&nbsp;&nbsp;FieldDescriptorProto_Type_TYPE_INT64 = = 3,<br>&nbsp;&nbsp;FieldDescriptorProto_Type_TYPE_UINT64 = = 4,<br>&nbsp;&nbsp;FieldDescriptorProto_Type_TYPE_INT32 = = 5,<br>&nbsp;&nbsp;FieldDescriptorProto_Type_TYPE_FIXED64 = = 6,<br>&nbsp;&nbsp;FieldDescriptorProto_Type_TYPE_FIXED32 = = 7,<br>&nbsp;&nbsp;FieldDescriptorProto_Type_TYPE_BOOL = = 8,<br>&nbsp;&nbsp;FieldDescriptorProto_Type_TYPE_STRING = = 9,<br>&nbsp;&nbsp;FieldDescriptorProto_Type_TYPE_GROUP = = 10,<br>&nbsp;&nbsp;FieldDescriptorProto_Type_TYPE_MESSAGE = = 11,<br>&nbsp;&nbsp;FieldDescriptorProto_Type_TYPE_BYTES = = 12,<br>&nbsp;&nbsp;FieldDescriptorProto_Type_TYPE_UINT32 = = 13,<br>&nbsp;&nbsp;FieldDescriptorProto_Type_TYPE_ENUM = = 14,<br>&nbsp;&nbsp;FieldDescriptorProto_Type_TYPE_SFIXED32 = = 15,<br>&nbsp;&nbsp;FieldDescriptorProto_Type_TYPE_SFIXED64 = = 16,<br>&nbsp;&nbsp;FieldDescriptorProto_Type_TYPE_SINT32 = = 17,<br>&nbsp;&nbsp;FieldDescriptorProto_Type_TYPE_SINT64 = = 18<br>}</code></h3><div style="margin-left: 16px"><p></p><table><tr><td>FieldDescriptorProto_Type_TYPE_DOUBLE</td><td></td></tr><tr><td>FieldDescriptorProto_Type_TYPE_FLOAT</td><td></td></tr><tr><td>FieldDescriptorProto_Type_TYPE_INT64</td><td></td></tr><tr><td>FieldDescriptorProto_Type_TYPE_UINT64</td><td></td></tr><tr><td>FieldDescriptorProto_Type_TYPE_INT32</td><td></td></tr><tr><td>FieldDescriptorProto_Type_TYPE_FIXED64</td><td></td></tr><tr><td>FieldDescriptorProto_Type_TYPE_FIXED32</td><td></td></tr><tr><td>FieldDescriptorProto_Type_TYPE_BOOL</td><td></td></tr><tr><td>FieldDescriptorProto_Type_TYPE_STRING</td><td></td></tr><tr><td>FieldDescriptorProto_Type_TYPE_GROUP</td><td></td></tr><tr><td>FieldDescriptorProto_Type_TYPE_MESSAGE</td><td></td></tr><tr><td>FieldDescriptorProto_Type_TYPE_BYTES</td><td></td></tr><tr><td>FieldDescriptorProto_Type_TYPE_UINT32</td><td></td></tr><tr><td>FieldDescriptorProto_Type_TYPE_ENUM</td><td></td></tr><tr><td>FieldDescriptorProto_Type_TYPE_SFIXED32</td><td></td></tr><tr><td>FieldDescriptorProto_Type_TYPE_SFIXED64</td><td></td></tr><tr><td>FieldDescriptorProto_Type_TYPE_SINT32</td><td></td></tr><tr><td>FieldDescriptorProto_Type_TYPE_SINT64</td><td></td></tr></table></div> <hr><h3 id="FieldDescriptorProto_Label.details"><code>enum protobuf::FieldDescriptorProto_Label {<br>&nbsp;&nbsp;FieldDescriptorProto_Label_LABEL_OPTIONAL = = 1,<br>&nbsp;&nbsp;FieldDescriptorProto_Label_LABEL_REQUIRED = = 2,<br>&nbsp;&nbsp;FieldDescriptorProto_Label_LABEL_REPEATED = = 3<br>}</code></h3><div style="margin-left: 16px"><p></p><table><tr><td>FieldDescriptorProto_Label_LABEL_OPTIONAL</td><td></td></tr><tr><td>FieldDescriptorProto_Label_LABEL_REQUIRED</td><td></td></tr><tr><td>FieldDescriptorProto_Label_LABEL_REPEATED</td><td></td></tr></table></div> <hr><h3 id="FileOptions_OptimizeMode.details"><code>enum protobuf::FileOptions_OptimizeMode {<br>&nbsp;&nbsp;FileOptions_OptimizeMode_SPEED = = 1,<br>&nbsp;&nbsp;FileOptions_OptimizeMode_CODE_SIZE = = 2,<br>&nbsp;&nbsp;FileOptions_OptimizeMode_LITE_RUNTIME = = 3<br>}</code></h3><div style="margin-left: 16px"><p></p><table><tr><td>FileOptions_OptimizeMode_SPEED</td><td></td></tr><tr><td>FileOptions_OptimizeMode_CODE_SIZE</td><td></td></tr><tr><td>FileOptions_OptimizeMode_LITE_RUNTIME</td><td></td></tr></table></div> <hr><h3 id="FieldOptions_CType.details"><code>enum protobuf::FieldOptions_CType {<br>&nbsp;&nbsp;FieldOptions_CType_STRING = = 0,<br>&nbsp;&nbsp;FieldOptions_CType_CORD = = 1,<br>&nbsp;&nbsp;FieldOptions_CType_STRING_PIECE = = 2<br>}</code></h3><div style="margin-left: 16px"><p></p><table><tr><td>FieldOptions_CType_STRING</td><td></td></tr><tr><td>FieldOptions_CType_CORD</td><td></td></tr><tr><td>FieldOptions_CType_STRING_PIECE</td><td></td></tr></table></div> <hr><h3 id="FieldOptions_JSType.details"><code>enum protobuf::FieldOptions_JSType {<br>&nbsp;&nbsp;FieldOptions_JSType_JS_NORMAL = = 0,<br>&nbsp;&nbsp;FieldOptions_JSType_JS_STRING = = 1,<br>&nbsp;&nbsp;FieldOptions_JSType_JS_NUMBER = = 2<br>}</code></h3><div style="margin-left: 16px"><p></p><table><tr><td>FieldOptions_JSType_JS_NORMAL</td><td></td></tr><tr><td>FieldOptions_JSType_JS_STRING</td><td></td></tr><tr><td>FieldOptions_JSType_JS_NUMBER</td><td></td></tr></table></div> <hr><h3 id="MethodOptions_IdempotencyLevel.details"><code>enum protobuf::MethodOptions_IdempotencyLevel {<br>&nbsp;&nbsp;MethodOptions_IdempotencyLevel_IDEMPOTENCY_UNKNOWN = = 0,<br>&nbsp;&nbsp;MethodOptions_IdempotencyLevel_NO_SIDE_EFFECTS = = 1,<br>&nbsp;&nbsp;MethodOptions_IdempotencyLevel_IDEMPOTENT = = 2<br>}</code></h3><div style="margin-left: 16px"><p></p><table><tr><td>MethodOptions_IdempotencyLevel_IDEMPOTENCY_UNKNOWN</td><td></td></tr><tr><td>MethodOptions_IdempotencyLevel_NO_SIDE_EFFECTS</td><td></td></tr><tr><td>MethodOptions_IdempotencyLevel_IDEMPOTENT</td><td></td></tr></table></div>

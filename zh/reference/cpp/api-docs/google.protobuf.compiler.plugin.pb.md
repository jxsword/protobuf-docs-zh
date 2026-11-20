+++
title = "plugin.pb.h"
toc_hide = "true"
linkTitle = "C++"
description = "本节包含在 C++ 中使用 Protobuf 类的参考文档。"
type = "docs"
source_url = "https://protobuf.dev/reference/cpp/api-docs/google.protobuf.compiler.plugin.pb/"
upstream_commit = "f72a6a648b34e9e098cbce1519bc9c8139105d66"
translated_at = "2026-11-20"
status = "translated"
translator = "agent"
+++

<p><code>#include &lt;google/protobuf/compiler/plugin.pb.h&gt;<br>namespace <a href="#google.protobuf.compiler">google::protobuf::compiler</a></code></p><p>protoc 插件（plugin）的 API。</p><p>本文件定义了一组协议消息（message）类，它们构成了 protoc 代码生成器（code generator）插件的 API。  用 C++ 编写的插件应当基于 <a href="google.protobuf.compiler.plugin">plugin.h</a> 中的 API 来构建，而不是直接处理 protobuf 层面的 API，但用其他语言编写的插件将需要处理下面定义的原始消息。</p><p>协议编译器目前不支持自动生成的文档，因此本页不含各定义的描述。  本文件由协议编译器根据 <code>plugin.proto</code> 生成，其内容如下：</p>

<pre>// Protocol Buffers - Google 的数据交换格式
// 版权所有 2008 Google Inc.  保留所有权利。
// https://developers.google.com/protocol-buffers/
//
// 在满足下列条件的前提下，无论是否经过修改，
// 均允许以源码和二进制形式再分发和使用本软件，
// 具体条件如下：
//
//     * 源码的再分发必须保留上述版权声明、本条件清单以及
// 下面的免责声明。
//     * 二进制形式的再分发必须在随分发
// 提供的文档和/或其他材料中复现上述
// 版权声明、本条件清单以及下面的
// 免责声明。
//     * 未经事先明确的书面许可，不得使用 Google Inc. 的
// 名称或其贡献者的名称来认可或推广源自本软件的
// 派生产品。
//
// 本软件由版权持有者与贡献者"按原样"提供，
// 不提供任何明示或默示的担保，包括但不限于
// 对适销性与特定用途适用性的默示担保。
// 在任何情况下，无论是因合同、严格责任还是
// 侵权行为（包括疏忽或其他原因）以任何方式引起，
// 版权持有者或贡献者均不对任何直接、间接、附带、
// 特殊、惩戒性或后果性损害（包括但不限于替代商品
// 或服务的采购、使用、数据或利润的损失，或业务中断）
// 承担责任，无论该损害因何引起，也无论是基于
// 何种责任理论，即使已被告知发生此类损害的
// 可能性亦然。

// 作者：kenton@google.com（Kenton Varda）
//
// 警告：插件接口目前是实验性的（EXPERIMENTAL），
//   随时可能会有变更。
//
// protoc（又称协议编译器）可以通过插件进行扩展。插件是
// 一个从 stdin 读取 CodeGeneratorRequest、并向 stdout 写出
// CodeGeneratorResponse 的程序。
//
// 用 C++ 编写的插件可以使用 google/protobuf/compiler/plugin.h，
// 而不必处理这里定义的原始协议。
//
// 插件可执行文件只需放在 PATH 中的某个位置即可。插件应命名为
// "protoc-gen-$NAME"，这样当把
// "--${NAME}_out" 标志传给 protoc 时就会使用该插件。

syntax = "proto2";

package google.protobuf.compiler;
option java_package = "com.google.protobuf.compiler";
option java_outer_classname = "PluginProtos";

option go_package = "google.golang.org/protobuf/types/pluginpb";

import "google/protobuf/descriptor.proto";

// 协议编译器的版本号（version）。
message Version {
  optional int32 major = 1;
  optional int32 minor = 2;
  optional int32 patch = 3;
  // alpha、beta 或 rc 发布（release）的后缀，例如 "alpha-1"、"rc2"。主线
  // 稳定版发布时应为空。
  optional string suffix = 4;
}

// 编码后的 CodeGeneratorRequest 会被写入插件的 stdin。
message CodeGeneratorRequest {
  // 在命令行中显式列出的 .proto 文件。代码生成器
  // 只应为这些文件生成代码。每个文件的描述符（descriptor）
  // 将包含在下面的 proto_file 中。
  repeated string file_to_generate = 1;

  // 命令行传入的生成器参数。
  optional string parameter = 2;

  // files_to_generate 中所有文件及其全部导入内容的
  // FileDescriptorProto。这些文件按拓扑序出现，因此每个文件
  // 都出现在导入它的任何文件之前。
  //
  // protoc 保证所有 proto_files 都写在上面的字段之后，
  // 尽管从技术上讲，protobuf 线路格式（wire format）并不保证这一点。
  // 理论上，这可以让插件以流式方式接收 FileDescriptorProto，
  // 并逐个处理它们，而不必一次性把整个集合读入内存。
  // 然而，截至撰写本文时，protoc 一端并未做类似的优化——
  // 它会把所有字段一次性存储在内存中，
  // 然后再发送给插件。
  //
  // FileDescriptorProto 中字段与扩展（extension）的类型名始终是
  // 完全限定（fully-qualified）的。
  repeated FileDescriptorProto proto_file = 15;

  // 协议编译器的版本号。
  optional Version compiler_version = 3;

}

// 插件会把编码后的 CodeGeneratorResponse 写出到 stdout。
message CodeGeneratorResponse {
  // 错误消息。如果非空，表示代码生成失败。
  // 即使以这种方式报告错误，插件进程也应以状态码零退出。
  //
  // 此字段应用于指示 .proto 文件中那些导致代码生成器
  // 无法生成正确代码的错误。而表明 protoc 本身存在问题的错误——
  // 例如输入的 CodeGeneratorRequest 无法解析——
  // 则应通过向 stderr 写入一条消息并以非零状态码退出
  // 来报告。
  optional string error = 1;

  // 代码生成器所支持特性（feature）的位掩码。
  // 这是 Feature 枚举中各取值的按位"或"结果。
  optional uint64 supported_features = 2;

  // 与 code_generator.h 保持同步。
  enum Feature {
    FEATURE_NONE = 0;
    FEATURE_PROTO3_OPTIONAL = 1;
  }

  // 表示单个生成的文件。
  message File {
    // 文件名，相对于输出目录。名称不得包含 "." 或 ".." 组件，
    // 且必须是相对路径而不能是绝对路径（也就是说，
    // 文件不得位于输出目录之外）。必须使用 "/" 作为
    // 路径分隔符，而不是 "\"。
    //
    // 如果省略名称，内容将被追加到上一个文件。这使得生成器
    // 可以把大文件拆分成小块，并让生成的文本以流式方式回传给
    // protoc，从而大文件无需一次性完整驻留在内存中。请注意，
    // 截至撰写本文时，protoc 并未针对这一点做优化——
    // 它在把文件写入磁盘之前会先读取完整的
    // CodeGeneratorResponse。
    optional string name = 1;

// 如果非空，表示所指名的文件应当已经存在，
// 这里的内容将被插入到该文件中一个定义好的
// 插入点（insertion point）处。此特性允许一个
// 代码生成器扩展另一个代码生成器产生的输出。
// 原始生成器可以在文件中放置形如下式的特殊
// 注解来提供插入点：
//   @@protoc_insertion_point(NAME)
// 该注解所在行的前后可以有任意文本，
// 这使得它可以放在注释中。NAME 应替换为命名该
// 插入点的标识符——其他生成器将把它用作
// insertion_point。插入到此位置的内容会被放在
// 包含该插入点的那一行的正上方（因此对同一位置
// 的多次插入会按添加顺序依次出现）。双 @ 的用意
// 是让生成的代码不太可能偶然包含看似插入点的
// 内容。
//
// 例如，C++ 代码生成器会在它生成的 .pb.h 文件中
// 放置下面这一行：
//   // @@protoc_insertion_point(namespace_scope)
// 这一行位于文件的 package 命名空间作用域内，
// 但在任何具体类之外。这样，另一个插件就可以指定
// insertion_point "namespace_scope"，以生成应放置在
// 此作用域内的其他类或其他声明。
//
// 请注意，如果包含插入点的那一行以空白开头，
// 则同样的空白会被加到插入文本的每一行。
// 这对 Python 这类缩进有意义的语言很有用。
// 在这些语言中，插入点注释的缩进量应与插入的
// 代码所需的缩进量一致，以便代码在该上下文中
// 能正确工作。
//
// 生成初始文件的代码生成器与向其中插入内容的
// 代码生成器，必须都在 protoc 的一次调用中
// 运行。代码生成器按其在命令行中出现的
// 顺序执行。
//
// 如果存在 |insertion_point|，则 |name| 也必须存在。
optional string insertion_point = 2;

// 文件内容。
optional string content = 15;

// 描述被插入文件内容的信息。如果使用了插入点，
// 此信息会被适当地偏移并插入到所生成文件的
// 代码生成元数据中。
optional GeneratedCodeInfo generated_code_info = 16;

  }
  repeated File file = 15;
}
</pre><table width="100%"><tr><th colspan="2"><h3 style="margin-top: 4px">本文件中的类</h3></th></tr></table><table><tr><th colspan="2"><h3 style="margin-top: 4px">文件成员</h3><div style="font-style: italic; font-weight: normal;">这些定义不属于任何类。</div></th></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>const ::protobuf::internal::DescriptorTable</code></td><td style="border-left-width: 0px"id="descriptor_table_google_2fprotobuf_2fcompiler_2fplugin_2eproto"><div style="padding-left: 16px; text-indent: -16px"><code><b>descriptor_table_google_2fprotobuf_2fcompiler_2fplugin_2eproto</b></code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>PROTOBUF_NAMESPACE_CLOSE PROTOBUF_NAMESPACE_OPEN protobuf::compiler::CodeGeneratorRequest *</code></td><td style="border-left-width: 0px"id="Arena::CreateMaybeMessage< protobuf::compiler::CodeGeneratorRequest >"><div style="padding-left: 16px; text-indent: -16px"><code><b>Arena::CreateMaybeMessage< protobuf::compiler::CodeGeneratorRequest ></b>(Arena * )</code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>protobuf::compiler::CodeGeneratorResponse *</code></td><td style="border-left-width: 0px"id="Arena::CreateMaybeMessage< protobuf::compiler::CodeGeneratorResponse >"><div style="padding-left: 16px; text-indent: -16px"><code><b>Arena::CreateMaybeMessage< protobuf::compiler::CodeGeneratorResponse ></b>(Arena * )</code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>protobuf::compiler::CodeGeneratorResponse_File *</code></td><td style="border-left-width: 0px"id="Arena::CreateMaybeMessage< protobuf::compiler::CodeGeneratorResponse_File >"><div style="padding-left: 16px; text-indent: -16px"><code><b>Arena::CreateMaybeMessage< protobuf::compiler::CodeGeneratorResponse_File ></b>(Arena * )</code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>protobuf::compiler::Version *</code></td><td style="border-left-width: 0px"id="Arena::CreateMaybeMessage< protobuf::compiler::Version >"><div style="padding-left: 16px; text-indent: -16px"><code><b>Arena::CreateMaybeMessage< protobuf::compiler::Version ></b>(Arena * )</code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>const EnumDescriptor *</code></td><td style="border-left-width: 0px"id="GetEnumDescriptor< protobuf::compiler::CodeGeneratorResponse_Feature >"><div style="padding-left: 16px; text-indent: -16px"><code><b>GetEnumDescriptor< protobuf::compiler::CodeGeneratorResponse_Feature ></b>()</code></div></td></tr></table>

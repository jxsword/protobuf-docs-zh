

+++
title = "ruby_generator.h"
toc_hide = "true"
linkTitle = "C++"
description = "本节包含在 C++ 中使用 Protobuf 类的参考文档。"
type = "docs"
source_url = "https://protobuf.dev/reference/cpp/api-docs/google.protobuf.compiler.ruby_generator/"
upstream_commit = "f72a6a648b34e9e098cbce1519bc9c8139105d66"
translated_at = "2026-11-20"
status = "translated"
translator = "agent"
+++

<p><code>#include &lt;google/protobuf/compiler/ruby/ruby_generator.h&gt;<br>namespace <a href="#google.protobuf.compiler">google::protobuf::compiler::ruby</a></code></p><p>为给定的 .proto 文件（proto file）生成 Ruby 代码。 </p><table width="100%"><tr><th colspan="2"><h3 style="margin-top: 4px">本文件中的类</h3></th></tr><tr><td><div><code><a href="#Generator">Generator</a></code></div><div style="font-style: italic; margin-top: 4px; margin-left: 16px;">用于生成 Ruby Protobuf 类的 <a href='google.protobuf.compiler.code_generator#CodeGenerator'>CodeGenerator</a> 实现。 </div></td></tr></table><h2 id="Generator">class Generator: public <a href="google.protobuf.compiler.code_generator#CodeGenerator">CodeGenerator</a></h2><p><code>#include &lt;<a href="#">google/protobuf/compiler/ruby/ruby_generator.h</a>&gt;<br>namespace <a href="#google.protobuf.compiler">google::protobuf::compiler::ruby</a></code></p><p>用于生成 Ruby Protobuf 类的 <a href='google.protobuf.compiler.code_generator#CodeGenerator'>CodeGenerator</a> 实现。 </p><p>如果你创建自己的协议编译器二进制程序并希望它支持 Ruby 输出，可以在 main() 函数中，将这个 <a href='google.protobuf.compiler.code_generator#CodeGenerator'>CodeGenerator</a> 的实例注册到 <a href='google.protobuf.compiler.command_line_interface#CommandLineInterface'>CommandLineInterface</a> 来实现。 </p>

<table><tr><th colspan="2"><h3 style="margin-top: 4px">成员</h3></th></tr></table>

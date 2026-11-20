+++
title = "plugin.h"
toc_hide = "true"
linkTitle = "C++"
description = "本节包含在 C++ 中使用 Protobuf 类的参考文档。"
type = "docs"
source_url = "https://protobuf.dev/reference/cpp/api-docs/google.protobuf.compiler.plugin/"
upstream_commit = "f72a6a648b34e9e098cbce1519bc9c8139105d66"
translated_at = "2026-11-20"
status = "translated"
translator = "agent"
+++

<p><code>#include &lt;google/protobuf/compiler/plugin.h&gt;<br>namespace <a href="#google.protobuf.compiler">google::protobuf::compiler</a></code></p><p>以 C++ 编写的 protoc 代码生成器（code generator）插件（plugin）的前端（front-end）。 </p><p>要用 C++ 实现一个 protoc 插件，只需编写一个 <a href='google.protobuf.compiler.code_generator#CodeGenerator'>CodeGenerator</a> 的实现，然后创建一个类似如下所示的 main() 函数： </p>

<pre>int main(int argc, char* argv[]) {
  MyCodeGenerator generator;
  return google::protobuf::compiler::PluginMain(argc, argv, &amp;generator);
}</pre>

<p> 你必须将你的插件与 libprotobuf 和 libprotoc 链接。</p>

<p>PluginMain 的核心部分是针对 CodeGeneratorRequest 调用给定的 <a href='google.protobuf.compiler.code_generator#CodeGenerator'>CodeGenerator</a>，以生成 CodeGeneratorResponse。这部分逻辑被抽象出来并做成了函数 GenerateCode，以便复用——例如，可以用它实现一个 PluginMain 的变体，在把请求交给给定代码生成器之前，先对输入的 CodeGeneratorRequest 做一些预处理。</p>

<p>要让 protoc 使用该插件，可执行以下操作之一：</p>

<ul>
  <li>把插件二进制文件放在 PATH 中的某个位置，并将其命名为 "protoc-gen-NAME"（把 "NAME" 替换为你插件的名称）。随后，如果你在调用 protoc 时传入参数 &ndash;NAME_out=OUT_DIR（同样，把 "NAME" 替换为你插件的名称），protoc 就会调用你的插件来生成输出，输出内容将被放置在 OUT_DIR 中。</li>
  <li>
    <p>把插件二进制文件放在任意位置、使用任意名称，并向 protoc 传入 &ndash;plugin 参数来指向你的插件，如下所示： </p>
<pre>protoc --plugin=protoc-gen-NAME=path/to/mybinary --NAME_out=OUT_DIR</pre>
    <p> 在 Windows 上，务必带上 .exe 后缀： </p>
<pre>protoc --plugin=protoc-gen-NAME=path/to/mybinary.exe --NAME_out=OUT_DIR</pre>
  </li>
</ul>

<table width="100%"><tr><th colspan="2"><h3 style="margin-top: 4px">本文件中的类</h3></th></tr></table><table><tr><th colspan="2"><h3 style="margin-top: 4px">文件成员</h3><div style="font-style: italic; font-weight: normal;">这些定义不属于任何类。</div></th></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>int</code></td><td style="border-left-width: 0px"id="PluginMain"><div style="padding-left: 16px; text-indent: -16px"><code><b>PluginMain</b>(int argc, char * argv, const <a href='google.protobuf.compiler.code_generator#CodeGenerator'>CodeGenerator</a> * generator)</code></div><div style="font-style: italic; margin-top: 4px; margin-left: 16px;">为暴露给定代码生成器的 protoc 插件实现 main()。 </div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>bool</code></td><td style="border-left-width: 0px"id="GenerateCode"><div style="padding-left: 16px; text-indent: -16px"><code><b>GenerateCode</b>(const CodeGeneratorRequest &amp; request, const <a href='google.protobuf.compiler.code_generator#CodeGenerator'>CodeGenerator</a> &amp; generator, CodeGeneratorResponse * response, std::string * error_msg)</code></div><div style="font-style: italic; margin-top: 4px; margin-left: 16px;">使用给定的代码生成器生成代码。  <a href="#GenerateCode.details">更多…</a></div></td></tr></table> <hr><h3 id="GenerateCode.details"><code>bool compiler::GenerateCode(<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;const CodeGeneratorRequest &amp; request,<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;const <a href='google.protobuf.compiler.code_generator#CodeGenerator'>CodeGenerator</a> &amp; generator,<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;CodeGeneratorResponse * response,<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;std::string * error_msg)</code></h3><div style="margin-left: 16px"><p>使用给定的代码生成器生成代码。 </p><p>如果代码生成成功，则返回 true。如果代码生成失败，可能会填充 error_msg 来说明失败原因。 </p>
</div>

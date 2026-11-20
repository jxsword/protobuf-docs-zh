+++
title = "command_line_interface.h"
toc_hide = "true"
linkTitle = "C++"
description = "本节包含在 C++ 中使用 Protobuf 类的参考文档。"
type = "docs"
source_url = "https://protobuf.dev/reference/cpp/api-docs/google.protobuf.compiler.command_line_interface/"
upstream_commit = "f72a6a648b34e9e098cbce1519bc9c8139105d66"
translated_at = "2026-11-20"
status = "translated"
translator = "agent"
+++

<p><code>#include &lt;google/protobuf/compiler/command_line_interface.h&gt;<br>namespace <a href="#google.protobuf.compiler">google::protobuf::compiler</a></code></p><p>实现了 Protocol 编译器（Protocol Compiler）前端，使其可被为支持其他语言而编写的自定义编译器复用。 </p><table width="100%"><tr><th colspan="2"><h3 style="margin-top: 4px">本文件中的类</h3></th></tr><tr><td><div><code><a href="#CommandLineInterface">CommandLineInterface</a></code></div><div style="font-style: italic; margin-top: 4px; margin-left: 16px;">该类实现了协议编译器的命令行接口。 </div></td></tr></table><h2 id="CommandLineInterface">class CommandLineInterface</h2><p><code>#include &lt;<a href="#">google/protobuf/compiler/command_line_interface.h</a>&gt;<br>namespace <a href="#google.protobuf.compiler">google::protobuf::compiler</a></code></p><p>该类实现了协议编译器的命令行接口。 </p><p>它的设计目标是让创建支持你所选语言的自定义协议编译器变得非常容易。例如，如果你想创建一个自定义协议编译器二进制程序，让它既包含常规的 C++ 支持、又支持你自己的自定义输出 "Foo"，那么你需要编写一个实现 <a href='google.protobuf.compiler.code_generator#CodeGenerator'>CodeGenerator</a> 接口的类 "FooGenerator"，然后编写如下 main() 过程：</p>

<pre>int main(int argc, char* argv[]) {
  google::protobuf::compiler::CommandLineInterface cli;

  // 支持生成 C++ 源码与头文件。
  google::protobuf::compiler::cpp::CppGenerator cpp_generator;
  cli.RegisterGenerator("--cpp_out", &amp;cpp_generator,
    "Generate C++ source and header.");

  // 支持生成 Foo 代码。
  FooGenerator foo_generator;
  cli.RegisterGenerator("--foo_out", &amp;foo_generator,
    "Generate Foo file.");

  return cli.Run(argc, argv);
}</pre>

<p>编译器的调用语法形如： </p>

<pre>protoc --cpp_out=outdir --foo_out=outdir --proto_path=src src/foo.proto</pre>

<p>要编译的 .proto 文件既可以用其物理文件路径在命令行上指定，也可以用相对于 &ndash;proto_path 所指定目录的虚拟路径指定。例如，对于 src/foo.proto，以下两种 protoc 调用方式效果相同： </p>

<pre>1. protoc --proto_path=src src/foo.proto (物理文件路径)
2. protoc --proto_path=src foo.proto (相对于 src 的虚拟路径)</pre>

<p>如果某个文件路径既可以解释为物理文件路径，又可以解释为相对虚拟路径，则以物理文件路径优先。</p>

<p>有关命令行语法的完整说明，请用 &ndash;help 调用它。 </p>

<table><tr><th colspan="2"><h3 style="margin-top: 4px">成员</h3></th></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>const char *const</code></td><td style="border-left-width: 0px"id="CommandLineInterface.kPathSeparator"><div style="padding-left: 16px; text-indent: -16px"><code><b>kPathSeparator</b></code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code></code></td><td style="border-left-width: 0px"id="CommandLineInterface.CommandLineInterface"><div style="padding-left: 16px; text-indent: -16px"><code><b>CommandLineInterface</b>()</code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code></code></td><td style="border-left-width: 0px"id="CommandLineInterface.~CommandLineInterface"><div style="padding-left: 16px; text-indent: -16px"><code><b>~CommandLineInterface</b>()</code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>void</code></td><td style="border-left-width: 0px"id="CommandLineInterface.RegisterGenerator"><div style="padding-left: 16px; text-indent: -16px"><code><b>RegisterGenerator</b>(const std::string &amp; flag_name, <a href='google.protobuf.compiler.code_generator#CodeGenerator'>CodeGenerator</a> * generator, const std::string &amp; help_text)</code></div><div style="font-style: italic; margin-top: 4px; margin-left: 16px;">为一种语言注册代码生成器（code generator）。  <a href="#CommandLineInterface.RegisterGenerator.details">更多…</a></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>void</code></td><td style="border-left-width: 0px"id="CommandLineInterface.RegisterGenerator"><div style="padding-left: 16px; text-indent: -16px"><code><b>RegisterGenerator</b>(const std::string &amp; flag_name, const std::string &amp; option_flag_name, <a href='google.protobuf.compiler.code_generator#CodeGenerator'>CodeGenerator</a> * generator, const std::string &amp; help_text)</code></div><div style="font-style: italic; margin-top: 4px; margin-left: 16px;">为一种语言注册代码生成器。  <a href="#CommandLineInterface.RegisterGenerator.details">更多…</a></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>void</code></td><td style="border-left-width: 0px"id="CommandLineInterface.AllowPlugins"><div style="padding-left: 16px; text-indent: -16px"><code><b>AllowPlugins</b>(const std::string &amp; exe_name_prefix)</code></div><div style="font-style: italic; margin-top: 4px; margin-left: 16px;">启用“插件”（plugin）。  <a href="#CommandLineInterface.AllowPlugins.details">更多…</a></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>int</code></td><td style="border-left-width: 0px"id="CommandLineInterface.Run"><div style="padding-left: 16px; text-indent: -16px"><code><b>Run</b>(int argc, const char *const argv)</code></div><div style="font-style: italic; margin-top: 4px; margin-left: 16px;">以给定的命令行参数运行 Protocol 编译器。  <a href="#CommandLineInterface.Run.details">更多…</a></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>void</code></td><td style="border-left-width: 0px"id="CommandLineInterface.SetInputsAreProtoPathRelative"><div style="padding-left: 16px; text-indent: -16px"><code><b>SetInputsAreProtoPathRelative</b>(bool )</code></div><div style="font-style: italic; margin-top: 4px; margin-left: 16px;">已弃用（deprecated）。  <a href="#CommandLineInterface.SetInputsAreProtoPathRelative.details">更多…</a></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>void</code></td><td style="border-left-width: 0px"id="CommandLineInterface.SetVersionInfo"><div style="padding-left: 16px; text-indent: -16px"><code><b>SetVersionInfo</b>(const std::string &amp; text)</code></div><div style="font-style: italic; margin-top: 4px; margin-left: 16px;">提供一段版本（version）说明文本，会在使用 &ndash;version 标志时打印。  <a href="#CommandLineInterface.SetVersionInfo.details">更多…</a></div></td></tr></table> <hr><h3 id="CommandLineInterface.RegisterGenerator.details"><code>void CommandLineInterface::RegisterGenerator(<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;const std::string &amp; flag_name,<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<a href='google.protobuf.compiler.code_generator#CodeGenerator'>CodeGenerator</a> * generator,<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;const std::string &amp; help_text)</code></h3><div style="margin-left: 16px"><p>为一种语言注册代码生成器。 </p><p>参数：</p>
<ul>
  <li>flag_name：用于指定此类输出文件的命令行标志。名称必须以 '-' 开头。如果名称长于一个字母，则必须以两个 '-' 开头。</li>
  <li>generator：将被调用以生成此类文件的 <a href='google.protobuf.compiler.code_generator#CodeGenerator'>CodeGenerator</a>。</li>
  <li>help_text：在 &ndash;help 输出中描述此标志的文本。</li>
</ul>
<p>某些生成器接受额外参数。你可以在命令行上指定该参数，方法是把它放在输出目录之前并以冒号分隔： </p>
<pre>protoc --foo_out=enable_bar:outdir</pre>
<p> 冒号之前的文本会作为“parameter”传给 <a href='google.protobuf.compiler.code_generator#CodeGenerator.Generate'>CodeGenerator::Generate()</a>。 </p>
</div> <hr><h3 id="CommandLineInterface.RegisterGenerator.details"><code>void CommandLineInterface::RegisterGenerator(<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;const std::string &amp; flag_name,<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;const std::string &amp; option_flag_name,<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<a href='google.protobuf.compiler.code_generator#CodeGenerator'>CodeGenerator</a> * generator,<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;const std::string &amp; help_text)</code></h3><div style="margin-left: 16px"><p>为一种语言注册代码生成器。 </p><p>除 flag_name 之外，你还可以指定另一个 option_flag_name，用于向已注册的代码生成器传递额外参数。假设你已通过如下调用注册了一个生成器： </p>
<pre>command_line_interface.RegisterGenerator("--foo_out", "--foo_opt", ...)</pre>
<p> 然后就可以用如下命令调用编译器： </p>
<pre>protoc --foo_out=enable_bar:outdir --foo_opt=enable_baz</pre>
<p> 这会把 "enable_bar,enable_baz" 作为参数传给生成器。 </p>
</div> <hr><h3 id="CommandLineInterface.AllowPlugins.details"><code>void CommandLineInterface::AllowPlugins(<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;const std::string &amp; exe_name_prefix)</code></h3><div style="margin-left: 16px"><p>启用“插件”。 </p><p>在此模式下，如果某个命令行标志以 "_out" 结尾但不匹配任何已注册的生成器，编译器会尝试寻找一个“插件”来实现该生成器。插件就是可执行文件。它们应位于 PATH 中的某个位置。</p>
<p>编译器把 exe_name_prefix 与未识别的标志名拼接并去掉 "_out"，以此确定要搜索的可执行文件名。例如，如果 exe_name_prefix 为 "protoc-"，而你传入标志 &ndash;foo_out，编译器将尝试运行程序 "protoc-gen-foo"。</p>
<p>插件程序应实现如下用法： </p>
<pre>plugin [--out=OUTDIR] [--parameter=PARAMETER] PROTO_FILES &lt; DESCRIPTORS</pre>
<p>&ndash;out 表示输出目录（即传给 &ndash;foo_out 参数的那个目录）；如果省略，则应使用当前目录。&ndash;parameter 给出生成器参数（如果提供了的话，见下文）。PROTO_FILES 列出在编译器命令行上给出的 .proto 文件；插件应为这些文件生成输出代码。最后，DESCRIPTORS 是一个编码后的 FileDescriptorSet（如 descriptor.proto 中所定义）。它会通过管道输入到插件的标准输入。该集合将包含 PROTO_FILES 中所列全部文件以及它们所导入的全部文件的描述符。插件绝不能尝试直接读取 PROTO_FILES &ndash; 它必须使用 FileDescriptorSet。</p>
<p>插件应像常规代码生成器那样生成一切必要的文件。它应把所生成的所有文件的名称写入 stdout。这些名称应相对于输出目录，而不是绝对路径，也不是相对于当前目录。如果发生任何错误，应把错误信息写入 stderr。如果错误是致命的，插件应以非零退出码退出。</p>
<p>插件可以拥有与常规内置生成器类似的生成器参数。额外的生成器参数可以通过与之匹配的 "_opt" 参数传入。例如： </p>
<pre>protoc --plug_out=enable_bar:outdir --plug_opt=enable_baz</pre>
<p> 这会把 "enable_bar,enable_baz" 作为参数传给插件。 </p>
</div> <hr><h3 id="CommandLineInterface.Run.details"><code>int CommandLineInterface::Run(<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;int argc,<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;const char *const argv)</code></h3><div style="margin-left: 16px"><p>以给定的命令行参数运行 Protocol 编译器。 </p><p>返回应由 main() 返回的错误码。</p>
<p>在多线程环境中调用 <a href='#CommandLineInterface.Run'>Run()</a> 可能不安全，因为它会调用 strerror()。不过我也不确定你为什么会想这么做。 </p>
</div> <hr><h3 id="CommandLineInterface.SetInputsAreProtoPathRelative.details"><code>void CommandLineInterface::SetInputsAreProtoPathRelative(<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;bool )</code></h3><div style="margin-left: 16px"><p>已弃用。 </p><p>调用此方法没有任何效果。Protocol 编译器现在总是会先相对于当前目录查找 .proto 文件；如果找不到该文件，则把输入路径当作虚拟路径处理。 </p>
</div> <hr><h3 id="CommandLineInterface.SetVersionInfo.details"><code>void CommandLineInterface::SetVersionInfo(<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;const std::string &amp; text)</code></h3><div style="margin-left: 16px"><p>提供一段版本（version）说明文本，会在使用 &ndash;version 标志时打印。 </p><p>在此文本之后的下一行，还会打印出 libprotoc 的版本。 </p>
</div>

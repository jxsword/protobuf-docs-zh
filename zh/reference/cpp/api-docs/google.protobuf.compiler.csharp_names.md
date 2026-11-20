+++
title = "csharp_names.h"
toc_hide = "true"
linkTitle = "C++"
description = "本节包含在 C++ 中使用 Protobuf 类的参考文档。"
type = "docs"
source_url = "https://protobuf.dev/reference/cpp/api-docs/google.protobuf.compiler.csharp_names/"
upstream_commit = "f72a6a648b34e9e098cbce1519bc9c8139105d66"
translated_at = "2026-11-20"
status = "translated"
translator = "agent"
+++

<p><code>#include &lt;google/protobuf/compiler/csharp/csharp_names.h&gt;<br>namespace <a href="#google.protobuf.compiler">google::protobuf::compiler::csharp</a></code></p><p>提供一种机制，将描述符（descriptor）映射为对应 C# 类的完全限定（fully-qualified）名称。 </p><table width="100%"><tr><th colspan="2"><h3 style="margin-top: 4px">本文件中的类</h3></th></tr></table><table><tr><th colspan="2"><h3 style="margin-top: 4px">文件成员</h3><div style="font-style: italic; font-weight: normal;">这些定义不属于任何类。</div></th></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>std::string</code></td><td style="border-left-width: 0px"id="GetFileNamespace"><div style="padding-left: 16px; text-indent: -16px"><code><b>GetFileNamespace</b>(const <a href='google.protobuf.descriptor#FileDescriptor'>FileDescriptor</a> * descriptor)</code></div><div style="font-style: italic; margin-top: 4px; margin-left: 16px;">前置条件：  <a href="#GetFileNamespace.details">更多…</a></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>std::string</code></td><td style="border-left-width: 0px"id="GetClassName"><div style="padding-left: 16px; text-indent: -16px"><code><b>GetClassName</b>(const <a href='google.protobuf.descriptor#Descriptor'>Descriptor</a> * descriptor)</code></div><div style="font-style: italic; margin-top: 4px; margin-left: 16px;">前置条件：  <a href="#GetClassName.details">更多…</a></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>std::string</code></td><td style="border-left-width: 0px"id="GetReflectionClassName"><div style="padding-left: 16px; text-indent: -16px"><code><b>GetReflectionClassName</b>(const <a href='google.protobuf.descriptor#FileDescriptor'>FileDescriptor</a> * descriptor)</code></div><div style="font-style: italic; margin-top: 4px; margin-left: 16px;">前置条件：  <a href="#GetReflectionClassName.details">更多…</a></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>std::string</code></td><td style="border-left-width: 0px"id="GetOutputFile"><div style="padding-left: 16px; text-indent: -16px"><code><b>GetOutputFile</b>(const <a href='google.protobuf.descriptor#FileDescriptor'>FileDescriptor</a> * descriptor, const std::string file_extension, const bool generate_directories, const std::string base_namespace, std::string * error)</code></div><div style="font-style: italic; margin-top: 4px; margin-left: 16px;">为给定的文件描述符生成输出文件名。  <a href="#GetOutputFile.details">更多…</a></div></td></tr></table> <hr><h3 id="GetFileNamespace.details"><code>std::string csharp::GetFileNamespace(<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;const <a href='google.protobuf.descriptor#FileDescriptor'>FileDescriptor</a> * descriptor)</code></h3><div style="margin-left: 16px"><p>前置条件：</p><pre>descriptor != NULL</pre>
<p>返回：</p>

<pre>给定文件描述符应使用的命名空间。</pre>
</div> <hr><h3 id="GetClassName.details"><code>std::string csharp::GetClassName(<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;const <a href='google.protobuf.descriptor#Descriptor'>Descriptor</a> * descriptor)</code></h3><div style="margin-left: 16px"><p>前置条件：</p><pre>descriptor != NULL</pre>

<p>返回：</p>

<pre>C# 类的完全限定名称。</pre>
</div> <hr><h3 id="GetReflectionClassName.details"><code>std::string csharp::GetReflectionClassName(<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;const <a href='google.protobuf.descriptor#FileDescriptor'>FileDescriptor</a> * descriptor)</code></h3><div style="margin-left: 16px"><p>前置条件：</p><pre>descriptor != NULL</pre>

<p>返回：</p>

<pre>提供对文件描述符进行访问的 C# 类的完全限定名称。协议编译器
会为每个已处理的 .proto 文件生成这样的类。</pre>
</div> <hr><h3 id="GetOutputFile.details"><code>std::string csharp::GetOutputFile(<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;const <a href='google.protobuf.descriptor#FileDescriptor'>FileDescriptor</a> * descriptor,<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;const std::string file_extension,<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;const bool generate_directories,<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;const std::string base_namespace,<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;std::string * error)</code></h3><div style="margin-left: 16px"><p>为给定的文件描述符生成输出文件名。 </p><p>如果 generate_directories 为 true，输出文件将放在与文件命名空间（namespace）相对应的目录下。base_namespace 可用于剥除部分顶层目录。例如，对于命名空间为 "Bar.Foo" 且 base_namespace="Bar" 的文件，结果文件将放在 "Foo" 目录下（而不是 "Bar/Foo"）。</p>
<p>前置条件：</p>
<pre>descriptor != NULL
error != NULL</pre>

<p>返回：</p>

<pre>用作给定文件描述符输出文件的文件名。如果失败，此函数将返回
空字符串，且 error 参数中将包含错误消息。</pre>

</div>

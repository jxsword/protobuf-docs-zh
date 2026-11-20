+++
title = "service.h"
toc_hide = "true"
linkTitle = "C++"
description = "本节包含在 C++ 中使用 Protobuf 类的参考文档。"
type = "docs"
source_url = "https://protobuf.dev/reference/cpp/api-docs/google.protobuf.service/"
upstream_commit = "f72a6a648b34e9e098cbce1519bc9c8139105d66"
translated_at = "2026-11-20"
status = "translated"
translator = "agent"
+++

<p><code>#include &lt;google/protobuf/service.h&gt;<br>namespace <a href="#google.protobuf">google::protobuf</a></code></p><p>已弃用：本模块声明了 proto2 远程过程调用（RPC）服务（service）底层的抽象接口。 </p><p>这些接口旨在独立于任何特定的 RPC 实现，从而使 proto2 服务可以构建在各种实现之上。从 2.3.0 版本开始，RPC 实现不应再基于这些接口构建，而应改为提供代码生成器（code generator）插件（plugin），生成针对特定 RPC 实现的代码。这样，生成代码（generated code）可以更加契合所使用的实现，并避免不必要的间接层。</p>

<p>当你使用协议编译器编译服务（service）定义时，它会生成两个类：服务的抽象接口（其方法与服务定义相匹配）和一个"存根（stub）"实现。存根只是 <a href='#RpcChannel'>RpcChannel</a> 的一层类型安全包装，用来模拟服务的本地实现。</p>

<p>例如，下面的服务定义： </p>

<pre>service MyService {
  rpc Foo(MyRequest) returns(MyResponse);
}</pre>

<p> 会生成抽象接口 "MyService" 和类 "MyService::Stub"。你可以按如下方式实现一个 MyService： </p>

<pre>class MyServiceImpl : public MyService {
 public:
  MyServiceImpl() {}
  ~MyServiceImpl() {}

  // 实现 MyService ---------------------------------------

  void Foo(google::protobuf::RpcController* controller,
           const MyRequest* request,
           MyResponse* response,
           Closure* done) {
    // ... 读取 request 并填充 response ...
    done-&gt;Run();
  }
};</pre>

<p> 然后，你需要向远程过程调用（RPC）服务器实现注册一个 MyServiceImpl 实例。（具体做法取决于该实现。）</p>

<p>要调用远程的 MyServiceImpl，首先需要一条连接到它的 <a href='#RpcChannel'>RpcChannel</a>。如何构造通道同样取决于你的 RPC 实现。这里我们以假想的 "MyRpcChannel" 为例： </p>

<pre>MyRpcChannel channel("rpc:hostname:1234/myservice");
MyRpcController controller;
MyServiceImpl::Stub stub(&amp;channel);
FooRequest request;
FooResponse response;

// ... 填充 request ...

stub.Foo(&amp;controller, request, &amp;response, NewCallback(HandleResponse));</pre>

<p>关于线程安全：</p>

<p>不同的 RPC 实现可能对回调可以在哪些线程上运行、以及应用允许用哪些线程调用 RPC 系统做出不同的保证。可移植的软件应当随时准备好让回调在任意线程上被调用，但不应尝试从接收到回调的线程之外的任何线程调用 RPC 系统。不过现实一点说，简单的软件可能想使用单线程的 RPC 系统，而高端软件则会想使用多线程。RPC 实现应提供多种选择。 </p>

<table width="100%"><tr><th colspan="2"><h3 style="margin-top: 4px">本文件中的类</h3></th></tr><tr><td><div><code><a href="#Service">Service</a></code></div><div style="font-style: italic; margin-top: 4px; margin-left: 16px;">基于协议缓冲区的 RPC 服务的抽象基接口。 </div></td></tr><tr><td><div><code><a href="#RpcController">RpcController</a></code></div><div style="font-style: italic; margin-top: 4px; margin-left: 16px;">An <a href='#RpcController'>RpcController</a> 充当一次方法调用的中介。 </div></td></tr><tr><td><div><code><a href="#RpcChannel">RpcChannel</a></code></div><div style="font-style: italic; margin-top: 4px; margin-left: 16px;">RPC 通道的抽象接口。 </div></td></tr></table><h2 id="Service">class Service</h2><p><code>#include &lt;<a href="#">google/protobuf/service.h</a>&gt;<br>namespace <a href="#google.protobuf">google::protobuf</a></code></p><p>基于协议缓冲区的 RPC 服务的抽象基接口。 </p><p>服务本身是抽象接口（由服务器实现，或以存根形式实现），但它们会继承此基接口。此接口的方法可用于调用 <a href='#Service'>Service</a> 的方法，而无需在编译期知晓其确切类型（类似于反射（reflection）<a href='google.protobuf.message#Reflection'>Reflection</a>）。 </p>
<table><tr><th colspan="2"><h3 style="margin-top: 4px">成员</h3></th></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>enum</code></td><td style="border-left-width: 0px"id="Service.ChannelOwnership"><div style="padding-left: 16px; text-indent: -16px"><code><b>ChannelOwnership</b></code></div><div style="font-style: italic; margin-top: 4px; margin-left: 16px;">构造存根时，你可以把 STUB_OWNS_CHANNEL 作为第二个参数传给构造函数，告诉它在销毁时删除其 <a href='#RpcChannel'>RpcChannel</a>。  <a href="#Service.ChannelOwnership.details">更多…</a></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code></code></td><td style="border-left-width: 0px"id="Service.Service"><div style="padding-left: 16px; text-indent: -16px"><code><b>Service</b>()</code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>virtual </code></td><td style="border-left-width: 0px"id="Service.~Service"><div style="padding-left: 16px; text-indent: -16px"><code><b>~Service</b>()</code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>virtual const <a href='google.protobuf.descriptor#ServiceDescriptor'>ServiceDescriptor</a> *</code></td><td style="border-left-width: 0px"id="Service.GetDescriptor"><div style="padding-left: 16px; text-indent: -16px"><code><b>GetDescriptor</b>()  = 0</code></div><div style="font-style: italic; margin-top: 4px; margin-left: 16px;">获取描述此服务及其方法的 <a href='google.protobuf.descriptor#ServiceDescriptor'>ServiceDescriptor</a>。 </div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>virtual void</code></td><td style="border-left-width: 0px"id="Service.CallMethod"><div style="padding-left: 16px; text-indent: -16px"><code><b>CallMethod</b>(const <a href='google.protobuf.descriptor#MethodDescriptor'>MethodDescriptor</a> * method, <a href='#RpcController'>RpcController</a> * controller, const <a href='google.protobuf.message#Message'>Message</a> * request, <a href='google.protobuf.message#Message'>Message</a> * response, Closure * done)  = 0</code></div><div style="font-style: italic; margin-top: 4px; margin-left: 16px;">调用由 <a href='google.protobuf.descriptor#MethodDescriptor'>MethodDescriptor</a> 指定的服务方法。  <a href="#Service.CallMethod.details">更多…</a></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>virtual const <a href='google.protobuf.message#Message'>Message</a> &amp;</code></td><td style="border-left-width: 0px"id="Service.GetRequestPrototype"><div style="padding-left: 16px; text-indent: -16px"><code><b>GetRequestPrototype</b>(const <a href='google.protobuf.descriptor#MethodDescriptor'>MethodDescriptor</a> * method) const  = 0</code></div><div style="font-style: italic; margin-top: 4px; margin-left: 16px;"><a href='#Service.CallMethod'>CallMethod()</a> 要求传入的 request 和 response 属于消息（message）<a href='google.protobuf.message#Message'>Message</a> 的某个特定子类。  <a href="#Service.GetRequestPrototype.details">更多…</a></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>virtual const <a href='google.protobuf.message#Message'>Message</a> &amp;</code></td><td style="border-left-width: 0px"id="Service.GetResponsePrototype"><div style="padding-left: 16px; text-indent: -16px"><code><b>GetResponsePrototype</b>(const <a href='google.protobuf.descriptor#MethodDescriptor'>MethodDescriptor</a> * method) const  = 0</code></div></td></tr></table> <hr><h3 id="Service.ChannelOwnership.details"><code>enum Service::ChannelOwnership {<br>&nbsp;&nbsp;STUB_OWNS_CHANNEL,<br>&nbsp;&nbsp;STUB_DOESNT_OWN_CHANNEL<br>}</code></h3><div style="margin-left: 16px"><p>构造存根时，你可以把 STUB_OWNS_CHANNEL 作为第二个参数传给构造函数，告诉它在销毁时删除其 <a href='#RpcChannel'>RpcChannel</a>。 </p><table><tr><td>STUB_OWNS_CHANNEL</td><td></td></tr><tr><td>STUB_DOESNT_OWN_CHANNEL</td><td></td></tr></table></div> <hr><h3 id="Service.CallMethod.details"><code>virtual void Service::CallMethod(<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;const <a href='google.protobuf.descriptor#MethodDescriptor'>MethodDescriptor</a> * method,<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<a href='#RpcController'>RpcController</a> * controller,<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;const <a href='google.protobuf.message#Message'>Message</a> * request,<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<a href='google.protobuf.message#Message'>Message</a> * response,<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Closure * done)  = 0</code></h3><div style="margin-left: 16px"><p>调用由 <a href='google.protobuf.descriptor#MethodDescriptor'>MethodDescriptor</a> 指定的服务方法。 </p><p>这通常实现为一个简单的 switch()，由它调用服务各方法的标准定义。</p>
<p>前置条件：</p>
<ul>
  <li>method-&gt;service() == <a href='#Service.GetDescriptor'>GetDescriptor()</a></li>
  <li>request 和 response 的类必须与 GetRequestPrototype(method) 和 GetResponsePrototype(method) 所返回对象的类完全相同。</li>
  <li>调用开始之后，在调用 "done" 之前，不得修改 request，也不得访问 response。</li>
  <li>"controller" 的类型必须与此 <a href='#Service'>Service</a> 所用 RPC 实现要求的类型相符。对于存根，"正确的类型"取决于存根所使用的 <a href='#RpcChannel'>RpcChannel</a>。服务器端的 <a href='#Service'>Service</a> 实现应当接受服务器端 RPC 实现所用的任何类型的 <a href='#RpcController'>RpcController</a>。</li>
</ul>
<p>后置条件：</p>
<ul>
  <li>方法完成后会调用 "done"。这可能发生在 <a href='#Service.CallMethod'>CallMethod()</a> 返回之前，也可能发生在未来的某个时刻。</li>
  <li>如果 RPC 成功，"response" 中包含服务器返回的响应。</li>
  <li>如果 RPC 失败，"response" 的内容是未定义的。可以查询 <a href='#RpcController'>RpcController</a> 来确定是否发生了错误，并可能获得关于该错误的更多信息。 </li>
</ul>
</div> <hr><h3 id="Service.GetRequestPrototype.details"><code>virtual const <a href='google.protobuf.message#Message'>Message</a> &amp; Service::GetRequestPrototype(<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;const <a href='google.protobuf.descriptor#MethodDescriptor'>MethodDescriptor</a> * method) const  = 0</code></h3><div style="margin-left: 16px"><p><a href='#Service.CallMethod'>CallMethod()</a> 要求传入的 request 和 response 属于 <a href='google.protobuf.message#Message'>Message</a> 的某个特定子类。 </p><p><a href='#Service.GetRequestPrototype'>GetRequestPrototype()</a> 与 GetResponsePrototype() 会获取这些所需类型的默认实例。然后你可以对这些实例调用 <a href='google.protobuf.message#Message.New'>Message::New()</a> 来构造可变对象，再将其传给 <a href='#Service.CallMethod'>CallMethod()</a>。</p>
<p>示例： </p>
<pre>const MethodDescriptor* method =
  service-&gt;GetDescriptor()-&gt;FindMethodByName("Foo");
Message* request  = stub-&gt;GetRequestPrototype (method)-&gt;New();
Message* response = stub-&gt;GetResponsePrototype(method)-&gt;New();
request-&gt;ParseFromString(input);
service-&gt;CallMethod(method, *request, response, callback);</pre>
</div><h2 id="RpcController">class RpcController</h2><p><code>#include &lt;<a href="#">google/protobuf/service.h</a>&gt;<br>namespace <a href="#google.protobuf">google::protobuf</a></code></p><p><a href='#RpcController'>RpcController</a> 充当一次方法调用的中介。 </p><p>controller 的主要用途是提供一种手段来操纵特定于 RPC 实现的设置，并获知 RPC 层面的错误。</p>
<p><a href='#RpcController'>RpcController</a> 接口提供的方法是一组"最小公共集"特性，我们期望所有实现都能支持它们。具体实现可以提供更高级的特性（例如截止时间传播）。 </p>
<table><tr><th colspan="2"><h3 style="margin-top: 4px">成员</h3></th></tr><tr><td style="border-right-width: 0px; text-align: right;"><code></code></td><td style="border-left-width: 0px"id="RpcController.RpcController"><div style="padding-left: 16px; text-indent: -16px"><code><b>RpcController</b>()</code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>virtual </code></td><td style="border-left-width: 0px"id="RpcController.~RpcController"><div style="padding-left: 16px; text-indent: -16px"><code><b>~RpcController</b>()</code></div></td></tr><tr><th colspan="2"><h3 style="margin-top: 4px; margin-bottom: 4px;">客户端方法</h3><div style="font-style: italic; font-weight: normal;">这些调用只能从客户端一侧发起。在服务器一侧，其结果是未定义的（可能崩溃）。 </div></th></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>virtual void</code></td><td style="border-left-width: 0px"id="RpcController.Reset"><div style="padding-left: 16px; text-indent: -16px"><code><b>Reset</b>()  = 0</code></div><div style="font-style: italic; margin-top: 4px; margin-left: 16px;">把 <a href='#RpcController'>RpcController</a> 重置到初始状态，以便在新调用中复用。  <a href="#RpcController.Reset.details">更多…</a></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>virtual bool</code></td><td style="border-left-width: 0px"id="RpcController.Failed"><div style="padding-left: 16px; text-indent: -16px"><code><b>Failed</b>() const  = 0</code></div><div style="font-style: italic; margin-top: 4px; margin-left: 16px;">调用结束后，如果该调用失败则返回 true。  <a href="#RpcController.Failed.details">更多…</a></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>virtual std::string</code></td><td style="border-left-width: 0px"id="RpcController.ErrorText"><div style="padding-left: 16px; text-indent: -16px"><code><b>ErrorText</b>() const  = 0</code></div><div style="font-style: italic; margin-top: 4px; margin-left: 16px;">如果 <a href='#RpcController.Failed'>Failed()</a> 为 true，则返回对错误的人类可读描述。 </div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>virtual void</code></td><td style="border-left-width: 0px"id="RpcController.StartCancel"><div style="padding-left: 16px; text-indent: -16px"><code><b>StartCancel</b>()  = 0</code></div><div style="font-style: italic; margin-top: 4px; margin-left: 16px;">告知 RPC 系统：调用者希望取消该 RPC 调用。  <a href="#RpcController.StartCancel.details">更多…</a></div></td></tr><tr><th colspan="2"><h3 style="margin-top: 4px; margin-bottom: 4px;">服务器端方法</h3><div style="font-style: italic; font-weight: normal;">
<p>这些调用只能从服务器一侧发起。</p>
<p>在客户端一侧，其结果是未定义的（可能崩溃）。 </p>
</div></th></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>virtual void</code></td><td style="border-left-width: 0px"id="RpcController.SetFailed"><div style="padding-left: 16px; text-indent: -16px"><code><b>SetFailed</b>(const std::string &amp; reason)  = 0</code></div><div style="font-style: italic; margin-top: 4px; margin-left: 16px;">使 <a href='#RpcController.Failed'>Failed()</a> 在客户端一侧返回 true。  <a href="#RpcController.SetFailed.details">更多…</a></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>virtual bool</code></td><td style="border-left-width: 0px"id="RpcController.IsCanceled"><div style="padding-left: 16px; text-indent: -16px"><code><b>IsCanceled</b>() const  = 0</code></div><div style="font-style: italic; margin-top: 4px; margin-left: 16px;">如果为 true，表示客户端已取消该 RPC，因此服务器不妨放弃对其应答。  <a href="#RpcController.IsCanceled.details">更多…</a></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>virtual void</code></td><td style="border-left-width: 0px"id="RpcController.NotifyOnCancel"><div style="padding-left: 16px; text-indent: -16px"><code><b>NotifyOnCancel</b>(Closure * callback)  = 0</code></div><div style="font-style: italic; margin-top: 4px; margin-left: 16px;">请求在 RPC 被取消时调用给定的回调。  <a href="#RpcController.NotifyOnCancel.details">更多…</a></div></td></tr></table> <hr><h3 id="RpcController.Reset.details"><code>virtual void RpcController::Reset()  = 0</code></h3><div style="margin-left: 16px"><p>把 <a href='#RpcController'>RpcController</a> 重置到初始状态，以便在新调用中复用。 </p><p>在 RPC 进行期间不得调用。 </p>
</div> <hr><h3 id="RpcController.Failed.details"><code>virtual bool RpcController::Failed() const  = 0</code></h3><div style="margin-left: 16px"><p>调用结束后，如果该调用失败则返回 true。 </p><p>失败的可能原因取决于 RPC 实现。在调用结束之前不得调用 <a href='#RpcController.Failed'>Failed()</a>。如果 <a href='#RpcController.Failed'>Failed()</a> 返回 true，响应消息的内容是未定义的。 </p>
</div> <hr><h3 id="RpcController.StartCancel.details"><code>virtual void RpcController::StartCancel()  = 0</code></h3><div style="margin-left: 16px"><p>告知 RPC 系统：调用者希望取消该 RPC 调用。 </p><p>RPC 系统可能立即取消它，可能等待一段时间之后再取消，也可能根本不取消该调用。如果调用被取消，"done" 回调仍会被调用，并且 <a href='#RpcController'>RpcController</a> 会在那时表明该调用已失败。 </p>
</div> <hr><h3 id="RpcController.SetFailed.details"><code>virtual void RpcController::SetFailed(<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;const std::string &amp; reason)  = 0</code></h3><div style="margin-left: 16px"><p>使 <a href='#RpcController.Failed'>Failed()</a> 在客户端一侧返回 true。 </p><p>"reason" 会被并入 <a href='#RpcController.ErrorText'>ErrorText()</a> 返回的消息中。如果你发现自己需要返回关于失败的机器可读信息，应当把它并入你的响应 Protobuf 消息，而不要调用 <a href='#RpcController.SetFailed'>SetFailed()</a>。 </p>
</div> <hr><h3 id="RpcController.IsCanceled.details"><code>virtual bool RpcController::IsCanceled() const  = 0</code></h3><div style="margin-left: 16px"><p>如果为 true，表示客户端已取消该 RPC，因此服务器不妨放弃对其应答。 </p><p>服务器仍应调用最终的 "done" 回调。 </p>
</div> <hr><h3 id="RpcController.NotifyOnCancel.details"><code>virtual void RpcController::NotifyOnCancel(<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Closure * callback)  = 0</code></h3><div style="margin-left: 16px"><p>请求在 RPC 被取消时调用给定的回调。 </p><p>该回调总是恰好被调用一次。如果 RPC 在未被取消的情况下完成，回调将在完成后被调用。如果在调用 <a href='#RpcController.NotifyOnCancel'>NotifyOnCancel()</a> 时 RPC 已经被取消，回调将被立即调用。</p>
<p>每个请求最多只能调用一次 <a href='#RpcController.NotifyOnCancel'>NotifyOnCancel()</a>。 </p>
</div><h2 id="RpcChannel">class RpcChannel</h2><p><code>#include &lt;<a href="#">google/protobuf/service.h</a>&gt;<br>namespace <a href="#google.protobuf">google::protobuf</a></code></p><p>RPC 通道的抽象接口。 </p><p><a href='#RpcChannel'>RpcChannel</a> 代表一条到某个 <a href='#Service'>Service</a> 的通信线路，可用于调用该 <a href='#Service'>Service</a> 的方法。该 <a href='#Service'>Service</a> 可能运行在另一台机器上。通常，你不应直接调用 <a href='#RpcChannel'>RpcChannel</a>，而应构造一个包装它的存根 <a href='#Service'>Service</a>。示例： </p>
<pre>RpcChannel* channel = new MyRpcChannel("remotehost.example.com:1234");
MyService* service = new MyService::Stub(channel);
service-&gt;MyMethod(request, &amp;response, callback);</pre>
<table><tr><th colspan="2"><h3 style="margin-top: 4px">成员</h3></th></tr><tr><td style="border-right-width: 0px; text-align: right;"><code></code></td><td style="border-left-width: 0px"id="RpcChannel.RpcChannel"><div style="padding-left: 16px; text-indent: -16px"><code><b>RpcChannel</b>()</code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>virtual </code></td><td style="border-left-width: 0px"id="RpcChannel.~RpcChannel"><div style="padding-left: 16px; text-indent: -16px"><code><b>~RpcChannel</b>()</code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>virtual void</code></td><td style="border-left-width: 0px"id="RpcChannel.CallMethod"><div style="padding-left: 16px; text-indent: -16px"><code><b>CallMethod</b>(const <a href='google.protobuf.descriptor#MethodDescriptor'>MethodDescriptor</a> * method, <a href='#RpcController'>RpcController</a> * controller, const <a href='google.protobuf.message#Message'>Message</a> * request, <a href='google.protobuf.message#Message'>Message</a> * response, Closure * done)  = 0</code></div><div style="font-style: italic; margin-top: 4px; margin-left: 16px;">调用远程服务的给定方法。  <a href="#RpcChannel.CallMethod.details">更多…</a></div></td></tr></table> <hr><h3 id="RpcChannel.CallMethod.details"><code>virtual void RpcChannel::CallMethod(<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;const <a href='google.protobuf.descriptor#MethodDescriptor'>MethodDescriptor</a> * method,<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<a href='#RpcController'>RpcController</a> * controller,<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;const <a href='google.protobuf.message#Message'>Message</a> * request,<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<a href='google.protobuf.message#Message'>Message</a> * response,<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Closure * done)  = 0</code></h3><div style="margin-left: 16px"><p>调用远程服务的给定方法。 </p><p>此过程的签名看起来与 <a href='#Service.CallMethod'>Service::CallMethod()</a> 相同，但要求在一个重要方面更为宽松：request 和 response 对象不必属于任何特定的类，只要它们的描述符（descriptor）是 method-&gt;input_type() 和 method-&gt;output_type() 即可。 </p>
</div>

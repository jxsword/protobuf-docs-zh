+++
title = "zero_copy_stream.h"
toc_hide = "true"
linkTitle = "C++"
description = "本节包含在 C++ 中使用 Protobuf 类的参考文档。"
type = "docs"
source_url = "https://protobuf.dev/reference/cpp/api-docs/google.protobuf.io.zero_copy_stream/"
upstream_commit = "f72a6a648b34e9e098cbce1519bc9c8139105d66"
translated_at = "2026-11-20"
status = "translated"
translator = "agent"
+++

<p><code>#include &lt;google/protobuf/io/zero_copy_stream.h&gt;<br>namespace <a href="#google.protobuf.io">google::protobuf::io</a></code></p><p>本文件包含 <a href='#ZeroCopyInputStream'>ZeroCopyInputStream</a> 与 <a href='#ZeroCopyOutputStream'>ZeroCopyOutputStream</a> 接口，它们表示抽象的 I/O 流，Protobuf 消息（message）既可以从中读取，也可以向其中写入。 </p><p>关于这些接口的几个简单实现，参见 <a href='google.protobuf.io.zero_copy_stream_impl'>zero_copy_stream_impl.h</a>。</p>

<p>这些接口与传统 I/O 流的不同之处在于：它们试图把需要完成的数据复制量降到最低。为此，分配缓冲区的职责被转移到流对象上，而不再由调用者承担。这样，流可以返回一个实际直接指向最终数据结构（字节将要存储之处）的缓冲区，调用者可以直接与该缓冲区交互，从而省去一次中间复制操作。</p>

<p>举个例子，考虑一个常见情形：你正在从一个已经位于内存中的数组（或者某个 mmap() 映射的文件）读取字节。使用传统 I/O 流时，你会这样写： </p>

<pre>char buffer[BUFFER_SIZE];
input-&gt;Read(buffer, BUFFER_SIZE);
DoSomething(buffer, BUFFER_SIZE);</pre>

<p> 此时，流基本上只是调用 memcpy() 把数据从数组复制到你的缓冲区。如果使用 <a href='#ZeroCopyInputStream'>ZeroCopyInputStream</a>，则应改为： </p>

<pre>const void* buffer;
int size;
input-&gt;Next(&amp;buffer, &amp;size);
DoSomething(buffer, size);</pre>

<p> 这里没有执行任何复制。输入流直接返回一个指向底层数组的指针，调用者最终直接从该数组读取。</p>

<p>如果你想以传统方式读取，可以创建一个包装这些对象的 <a href='google.protobuf.io.coded_stream#CodedInputStream'>CodedInputStream</a> 或 <a href='google.protobuf.io.coded_stream#CodedOutputStream'>CodedOutputStream</a>，并使用它们的 ReadRaw()/WriteRaw() 方法。这当然会增加一步复制，但 Coded*Stream 会负责缓冲处理，因此至少效率还算不错。</p>

<p><a href='#ZeroCopyInputStream'>ZeroCopyInputStream</a> 示例： </p>

<pre>// 读取一个文件，并将其内容打印到 stdout。
int fd = open("myfile", O_RDONLY);
ZeroCopyInputStream* input = new FileInputStream(fd);

const void* buffer;
int size;
while (input-&gt;Next(&amp;buffer, &amp;size)) {
  cout.write(buffer, size);
}

delete input;
close(fd);</pre>

<p><a href='#ZeroCopyOutputStream'>ZeroCopyOutputStream</a> 示例： </p>

<pre>// 把 "infile" 的内容复制到 "outfile"，对 "infile" 使用普通 read()，
// 而对 "outfile" 使用 ZeroCopyOutputStream。
int infd = open("infile", O_RDONLY);
int outfd = open("outfile", O_WRONLY);
ZeroCopyOutputStream* output = new FileOutputStream(outfd);

void* buffer;
int size;
while (output-&gt;Next(&amp;buffer, &amp;size)) {
  int bytes = read(infd, buffer, size);
  if (bytes &lt; size) {
    // 已到达 EOF。
    output-&gt;BackUp(size - bytes);
    break;
  }
}

delete output;
close(infd);
close(outfd);</pre>

<table width="100%"><tr><th colspan="2"><h3 style="margin-top: 4px">本文件中的类</h3></th></tr><tr><td><div><code><a href="#ZeroCopyInputStream">ZeroCopyInputStream</a></code></div><div style="font-style: italic; margin-top: 4px; margin-left: 16px;">一个类似于输入流的抽象接口，但为尽量减少复制而设计。 </div></td></tr><tr><td><div><code><a href="#ZeroCopyOutputStream">ZeroCopyOutputStream</a></code></div><div style="font-style: italic; margin-top: 4px; margin-left: 16px;">一个类似于输出流的抽象接口，但为尽量减少复制而设计。 </div></td></tr></table><h2 id="ZeroCopyInputStream">class ZeroCopyInputStream</h2><p><code>#include &lt;<a href="#">google/protobuf/io/zero_copy_stream.h</a>&gt;<br>namespace <a href="#google.protobuf.io">google::protobuf::io</a></code></p><p>一个类似于输入流的抽象接口，但为尽量减少复制而设计。 </p><p>已知子类：</p><ul><li><code><a href="google.protobuf.io.zero_copy_stream_impl_lite#ArrayInputStream">ArrayInputStream</a></code></li><li><code><a href="google.protobuf.io.zero_copy_stream_impl#ConcatenatingInputStream">ConcatenatingInputStream</a></code></li><li><code><a href="google.protobuf.io.zero_copy_stream_impl_lite#CopyingInputStreamAdaptor">CopyingInputStreamAdaptor</a></code></li><li><code><a href="google.protobuf.io.zero_copy_stream_impl#FileInputStream">FileInputStream</a></code></li><li><code><a href="google.protobuf.io.zero_copy_stream_impl#IstreamInputStream">IstreamInputStream</a></code></li><li><code><a href="google.protobuf.io.zero_copy_stream_impl_lite#LimitingInputStream">LimitingInputStream</a></code></li></ul><table><tr><th colspan="2"><h3 style="margin-top: 4px">成员</h3></th></tr><tr><td style="border-right-width: 0px; text-align: right;"><code></code></td><td style="border-left-width: 0px"id="ZeroCopyInputStream.ZeroCopyInputStream"><div style="padding-left: 16px; text-indent: -16px"><code><b>ZeroCopyInputStream</b>()</code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>virtual </code></td><td style="border-left-width: 0px"id="ZeroCopyInputStream.~ZeroCopyInputStream"><div style="padding-left: 16px; text-indent: -16px"><code><b>~ZeroCopyInputStream</b>()</code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>virtual bool</code></td><td style="border-left-width: 0px"id="ZeroCopyInputStream.Next"><div style="padding-left: 16px; text-indent: -16px"><code><b>Next</b>(const void ** data, int * size)  = 0</code></div><div style="font-style: italic; margin-top: 4px; margin-left: 16px;">从流中获取一块数据。  <a href="#ZeroCopyInputStream.Next.details">更多…</a></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>virtual void</code></td><td style="border-left-width: 0px"id="ZeroCopyInputStream.BackUp"><div style="padding-left: 16px; text-indent: -16px"><code><b>BackUp</b>(int count)  = 0</code></div><div style="font-style: italic; margin-top: 4px; margin-left: 16px;">回退若干字节，使得下一次调用 <a href='#ZeroCopyInputStream.Next'>Next()</a> 会再次返回上次调用 <a href='#ZeroCopyInputStream.Next'>Next()</a>。  <a href="#ZeroCopyInputStream.BackUp.details">更多…</a></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>virtual bool</code></td><td style="border-left-width: 0px"id="ZeroCopyInputStream.Skip"><div style="padding-left: 16px; text-indent: -16px"><code><b>Skip</b>(int count)  = 0</code></div><div style="font-style: italic; margin-top: 4px; margin-left: 16px;">跳过若干字节。  <a href="#ZeroCopyInputStream.Skip.details">更多…</a></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>virtual int64_t</code></td><td style="border-left-width: 0px"id="ZeroCopyInputStream.ByteCount"><div style="padding-left: 16px; text-indent: -16px"><code><b>ByteCount</b>() const  = 0</code></div><div style="font-style: italic; margin-top: 4px; margin-left: 16px;">返回自创建此对象以来读取的总字节数。 </div></td></tr></table> <hr><h3 id="ZeroCopyInputStream.Next.details"><code>virtual bool ZeroCopyInputStream::Next(<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;const void ** data,<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;int * size)  = 0</code></h3><div style="margin-left: 16px"><p>从流中获取一块数据。 </p><p>前置条件：</p>
<ul>
  <li>"size" 和 "data" 不得为 NULL。</li>
</ul>
<p>后置条件：</p>
<ul>
  <li>如果返回值为 false，表示没有更多数据可返回，或者发生了错误。所有错误都是永久性的。</li>
  <li>否则，"size" 指向实际读取的字节数，"data" 指向一个指针，该指针指向包含这些字节的缓冲区。</li>
  <li>此缓冲区的所有权仍属于流；缓冲区只在该流的其他某个方法被调用或流被销毁之前保持有效。</li>
  <li>只要反复调用 <a href='#ZeroCopyInputStream.Next'>Next()</a> 最终能返回非零大小的缓冲区，返回大小为零的缓冲区就是合法的。 </li>
</ul>
</div> <hr><h3 id="ZeroCopyInputStream.BackUp.details"><code>virtual void ZeroCopyInputStream::BackUp(<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;int count)  = 0</code></h3><div style="margin-left: 16px"><p>回退若干字节，使得下一次调用 <a href='#ZeroCopyInputStream.Next'>Next()</a> 会再次返回上次调用 <a href='#ZeroCopyInputStream.Next'>Next()</a>. </p><p>在编写只打算读取输入中某一位置之前的内容然后返回的过程时，这很有用。如果 <a href='#ZeroCopyInputStream.Next'>Next()</a> 返回的缓冲区超出了你想读取的范围，可以用 <a href='#ZeroCopyInputStream.BackUp'>BackUp()</a> 回退到你原本打算结束的位置。</p>
<p>前置条件：</p>
<ul>
  <li>最后调用的方法必须是 <a href='#ZeroCopyInputStream.Next'>Next()</a>。</li>
  <li>count 必须不超过上次调用 <a href='#ZeroCopyInputStream.Next'>Next()</a>。</li>
</ul>
<p>后置条件：</p>
<ul>
  <li>上次调用 <a href='#ZeroCopyInputStream.Next'>Next()</a> 所返回的最后一个缓冲区的最后 "count" 个字节会被退回流中。随后对 <a href='#ZeroCopyInputStream.Next'>Next()</a> 的调用会先再次返回相同的数据，然后才产生新数据。 </li>
</ul>
</div> <hr><h3 id="ZeroCopyInputStream.Skip.details"><code>virtual bool ZeroCopyInputStream::Skip(<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;int count)  = 0</code></h3><div style="margin-left: 16px"><p>跳过若干字节。 </p><p>如果到达流末尾或发生某种输入错误，则返回 false。在到达流末尾的情形下，流会前进到末尾（因此 <a href='#ZeroCopyInputStream.ByteCount'>ByteCount()</a> 会返回整个流的大小）。 </p>
</div><h2 id="ZeroCopyOutputStream">class ZeroCopyOutputStream</h2><p><code>#include &lt;<a href="#">google/protobuf/io/zero_copy_stream.h</a>&gt;<br>namespace <a href="#google.protobuf.io">google::protobuf::io</a></code></p><p>一个类似于输出流的抽象接口，但为尽量减少复制而设计。 </p><p>已知子类：</p><ul><li><code><a href="google.protobuf.io.zero_copy_stream_impl_lite#ArrayOutputStream">ArrayOutputStream</a></code></li><li><code><a href="google.protobuf.io.zero_copy_stream_impl_lite#CopyingOutputStreamAdaptor">CopyingOutputStreamAdaptor</a></code></li><li><code><a href="google.protobuf.io.zero_copy_stream_impl#OstreamOutputStream">OstreamOutputStream</a></code></li><li><code><a href="google.protobuf.io.zero_copy_stream_impl_lite#StringOutputStream">StringOutputStream</a></code></li></ul><table><tr><th colspan="2"><h3 style="margin-top: 4px">成员</h3></th></tr><tr><td style="border-right-width: 0px; text-align: right;"><code></code></td><td style="border-left-width: 0px"id="ZeroCopyOutputStream.ZeroCopyOutputStream"><div style="padding-left: 16px; text-indent: -16px"><code><b>ZeroCopyOutputStream</b>()</code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>virtual </code></td><td style="border-left-width: 0px"id="ZeroCopyOutputStream.~ZeroCopyOutputStream"><div style="padding-left: 16px; text-indent: -16px"><code><b>~ZeroCopyOutputStream</b>()</code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>virtual bool</code></td><td style="border-left-width: 0px"id="ZeroCopyOutputStream.Next"><div style="padding-left: 16px; text-indent: -16px"><code><b>Next</b>(void ** data, int * size)  = 0</code></div><div style="font-style: italic; margin-top: 4px; margin-left: 16px;">获取一个可写入数据的缓冲区。  <a href="#ZeroCopyOutputStream.Next.details">更多…</a></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>virtual void</code></td><td style="border-left-width: 0px"id="ZeroCopyOutputStream.BackUp"><div style="padding-left: 16px; text-indent: -16px"><code><b>BackUp</b>(int count)  = 0</code></div><div style="font-style: italic; margin-top: 4px; margin-left: 16px;">回退若干字节，使得上次调用 <a href='#ZeroCopyOutputStream.Next'>Next()</a> 所返回的最后一个缓冲区的末尾实际上不会被写入。  <a href="#ZeroCopyOutputStream.BackUp.details">更多…</a></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>virtual int64_t</code></td><td style="border-left-width: 0px"id="ZeroCopyOutputStream.ByteCount"><div style="padding-left: 16px; text-indent: -16px"><code><b>ByteCount</b>() const  = 0</code></div><div style="font-style: italic; margin-top: 4px; margin-left: 16px;">返回自创建此对象以来写入的总字节数。 </div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>virtual bool</code></td><td style="border-left-width: 0px"id="ZeroCopyOutputStream.WriteAliasedRaw"><div style="padding-left: 16px; text-indent: -16px"><code><b>WriteAliasedRaw</b>(const void * data, int size)</code></div><div style="font-style: italic; margin-top: 4px; margin-left: 16px;">将给定的一块数据写入输出。  <a href="#ZeroCopyOutputStream.WriteAliasedRaw.details">更多…</a></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>virtual bool</code></td><td style="border-left-width: 0px"id="ZeroCopyOutputStream.AllowsAliasing"><div style="padding-left: 16px; text-indent: -16px"><code><b>AllowsAliasing</b>() const</code></div></td></tr></table> <hr><h3 id="ZeroCopyOutputStream.Next.details"><code>virtual bool ZeroCopyOutputStream::Next(<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;void ** data,<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;int * size)  = 0</code></h3><div style="margin-left: 16px"><p>获取一个可写入数据的缓冲区。 </p><p>写入此缓冲区的任何数据最终（可能立即写入，也可能稍后写入）都会到达输出。</p>
<p>前置条件：</p>
<ul>
  <li>"size" 和 "data" 不得为 NULL。</li>
</ul>
<p>后置条件：</p>
<ul>
  <li>如果返回值为 false，表示发生了错误。所有错误都是永久性的。</li>
  <li>否则，"size" 指向缓冲区中的实际字节数，"data" 指向该缓冲区。</li>
  <li>此缓冲区的所有权仍属于流；缓冲区只在该流的其他某个方法被调用或流被销毁之前保持有效。</li>
  <li>调用者存入此缓冲区的任何数据最终都会被写入输出（除非调用了 <a href='#ZeroCopyOutputStream.BackUp'>BackUp()</a>）。</li>
  <li>只要反复调用 <a href='#ZeroCopyOutputStream.Next'>Next()</a> 最终能返回非零大小的缓冲区，返回大小为零的缓冲区就是合法的。 </li>
</ul>
</div> <hr><h3 id="ZeroCopyOutputStream.BackUp.details"><code>virtual void ZeroCopyOutputStream::BackUp(<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;int count)  = 0</code></h3><div style="margin-left: 16px"><p>回退若干字节，使得上次调用 <a href='#ZeroCopyOutputStream.Next'>Next()</a> 所返回的最后一个缓冲区的末尾实际上不会被写入。 </p><p>当你已完成写入所有想写入的数据、但最后一个缓冲区比实际所需更大时，就需要这一操作。你不希望在数据末尾之后写入一堆垃圾数据，所以用 <a href='#ZeroCopyOutputStream.BackUp'>BackUp()</a> 来回退。</p>
<p>前置条件：</p>
<ul>
  <li>最后调用的方法必须是 <a href='#ZeroCopyOutputStream.Next'>Next()</a>。</li>
  <li>count 必须不超过上次调用 <a href='#ZeroCopyOutputStream.Next'>Next()</a>。</li>
  <li>调用者必须尚未向该缓冲区的最后 "count" 个字节写入任何内容。</li>
</ul>
<p>后置条件：</p>
<ul>
  <li>上次调用 <a href='#ZeroCopyOutputStream.Next'>Next()</a> 所返回的最后一个缓冲区的最后 "count" 个字节将被忽略。 </li>
</ul>
</div> <hr><h3 id="ZeroCopyOutputStream.WriteAliasedRaw.details"><code>virtual bool ZeroCopyOutputStream::WriteAliasedRaw(<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;const void * data,<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;int size)</code></h3><div style="margin-left: 16px"><p>将给定的一块数据写入输出。 </p><p>某些输出流可能以避免复制的方式实现此方法。调用 <a href='#ZeroCopyOutputStream.WriteAliasedRaw'>WriteAliasedRaw()</a> 之前请先检查 AllowsAliasing()。在不允许别名的流上调用 <a href='#ZeroCopyOutputStream.WriteAliasedRaw'>WriteAliasedRaw()</a> 会触发 GOOGLE_CHECK 失败。</p>
<p>注意：调用者有责任确保这块内存在流消费完其中全部数据之前保持存活。 </p>
</div>

haven
=====

基于二进制、字符串协议的server。支持 gevent、threading。

python2, python3 supported

注意: 使用的Box，必须包含 cmd 字段


已知BUG:
1.
gevent模式下，当打开server的ssh连接被关闭时，由于SIGHUP被处理为忽略，所以不会进行任何处理，到这里是正常的。
但之后如果向master发送INT或者TERM信号，进程无法关闭。
调试看到父进程和子进程都正常接收到信号并处理了，但是进程没有退出，很是奇怪。

thread模式下正常。

# catm-python-lib

CAT-Mをもちいた研究に頻繁に使用するコードをまとめたリポジトリ。

### 回路シミュレーターについて

`src/catmlib/circuit`では`PySpice`を利用した回路のシミュレーションができるクラスがある。

ただし、それらのクラスを利用する場合は、あらかじめ`PySpice`をインストールする必要がある。
（すなわちコマンドラインで`ngspice`できる必要あり。）

MacOSなどでは以下でインストールできる。

```zsh
brew install ngspice
brew install --cask xquartz
```

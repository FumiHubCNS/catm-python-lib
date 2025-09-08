# catm-python-lib

CAT-Mをもちいた研究に頻繁に使用するコードをまとめたリポジトリ。


## 環境整備

筆者のサーバーやPCにインストールした時のログは以下のような感じです・

### Ubuntu 

```zsh
cd $HOME
mkdir -p source 
cd source 
curl -L https://github.com/astral-sh/uv/releases/latest/download/uv-x86_64-unknown-linux-gnu.tar.gz -o uv.tar.gz
tar -xvzf uv.tar.gz
echo export PATH="$HOME/source/uv-x86_64-unknown-linux-gnu/:\$PATH" >>  ~/.bashrc
source ~/.bashrc 
uv --version
```

### 回路シミュレーターについて

`src/catmlib/circuit`では`PySpice`を利用した回路のシミュレーションができるクラスがある。

ただし、それらのクラスを利用する場合は、あらかじめ`PySpice`をインストールする必要がある。
（すなわちコマンドラインで`ngspice`できる必要あり。）

MacOSなどでは以下でインストールできる。

```zsh
brew install ngspice
brew install --cask xquartz
```

Ubuntuでは以下

```zsh
sudo apt update
sudo apt install -y libngspice0 ngspice
sudo ln -s /usr/lib/x86_64-linux-gnu/libngspice.so.0 /usr/lib/x86_64-linux-gnu/libngspice.so
```

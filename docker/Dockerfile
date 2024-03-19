FROM ubuntu:18.04

RUN cp /etc/apt/sources.list /etc/apt/sources.list.bak && \
	# you may comment the following six lines if you don't need to use tsinghua mirror
	echo "deb http://mirrors.tuna.tsinghua.edu.cn/ubuntu/ bionic main restricted universe multiverse" > /etc/apt/sources.list && \
	echo "deb http://mirrors.tuna.tsinghua.edu.cn/ubuntu/ bionic-updates main restricted universe multiverse" >> /etc/apt/sources.list && \
	echo "deb http://mirrors.tuna.tsinghua.edu.cn/ubuntu/ bionic-backports main restricted universe multiverse" >> /etc/apt/sources.list && \
	echo "deb http://security.ubuntu.com/ubuntu/ bionic-security main restricted universe multiverse" >> /etc/apt/sources.list && \
	ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
	echo "Asia/Shanghai" > /etc/timezone && \
	apt-get clean && \
	apt-get update && \
	apt-get install -y sudo tmux htop git wget curl make gdb lsb-release build-essential

ARG current_path=.
ARG build_type=release

ENV SRC		/src
ENV OUT		/out
ENV SHARED 	/shared
ENV TRIAGE_BY_CASR /triage_by_casr
ENV COV /cov
ENV AFLSHOWMAP /aflshowmap

ENV CC  /usr/bin/gcc
ENV CXX /usr/bin/g++
ENV CFLAGS "-O0"
ENV CXXFLAGS "-O0"
ENV LD /usr/bin/ld
ENV AR /usr/bin/ar
ENV AS /usr/bin/as
ENV NM /usr/bin/nm
ENV RANLIB /usr/bin/ranlib

ARG USER_ID=1000
ARG GROUP_ID=1000
RUN mkdir -p /home && \
	groupadd -g ${GROUP_ID} hesitater && \
	useradd -l -u ${USER_ID} -K UMASK=0000 -d /home -g hesitater hesitater && \
	chown hesitater:hesitater /home
RUN	echo "hesitater:root" | chpasswd && usermod -a -G sudo hesitater && echo "hesitater ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

RUN mkdir -p ${SHARED} ${OUT} ${TRIAGE_BY_CASR} ${COV} ${AFLSHOWMAP} && \
	chown hesitater:hesitater ${SHARED} ${OUT} ${TRIAGE_BY_CASR} ${COV} ${AFLSHOWMAP} && \
	chmod 744 ${SHARED} ${OUT} ${TRIAGE_BY_CASR} ${COV} ${AFLSHOWMAP}

# RUN git clone --depth=1 https://github.com/vanhauser-thc/afl-cov && \
# 	(cd afl-cov && make install) && \
# 	rm -rf afl-cov

# ENV PATH=$PATH:${SRC}/cargo/bin
# ENV CARGO_HOME=${SRC}/cargo
# RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | \
# 	RUSTUP_DIST_SERVER=https://mirrors.ustc.edu.cn/rust-static RUSTUP_UPDATE_ROOT=https://mirrors.ustc.edu.cn/rust-static/rustup \
# 	sh -s -- -y && \
# 	mkdir -vp ${CARGO_HOME:-$HOME/.cargo} && \
# 	echo \
# 	"[source.crates-io]\nreplace-with = 'ustc'\n\n[source.ustc]\nregistry = 'git://mirrors.ustc.edu.cn/crates.io-index'" \
# 	>> ${CARGO_HOME:-$HOME/.cargo}/config && \
# 	cargo install casr

ARG fuzzer_name
ARG fuzzer_path=fuzzers/${fuzzer_name}
ENV FUZZER 	${SRC}/${fuzzer_path}
USER root:root
RUN mkdir -p ${FUZZER}
COPY --chown=hesitater:hesitater ${current_path}/${fuzzer_path} ${FUZZER}/
RUN chmod +x ${FUZZER}/*.sh
RUN ${FUZZER}/preinstall.sh
RUN chown hesitater:hesitater ${FUZZER}
USER hesitater:hesitater
RUN ${FUZZER}/fetch.sh
RUN ${FUZZER}/build.sh

ARG target_name
ARG target_path=targets/${target_name}
ENV TARGET 	${SRC}/${target_path}
USER root:root
RUN mkdir -p ${TARGET}
COPY --chown=hesitater:hesitater ${current_path}/${target_path} ${TARGET}/
RUN chmod +x ${TARGET}/*.sh
RUN ${TARGET}/preinstall.sh
RUN chown hesitater:hesitater ${TARGET}
USER hesitater:hesitater
RUN ${TARGET}/fetch.sh

RUN ${FUZZER}/instrument.sh

COPY --chown=hesitater:hesitater ${current_path}/fuzzdeploy/run.sh ${SRC}/run.sh
COPY --chown=hesitater:hesitater ${current_path}/fuzzdeploy/scripts ${SRC}/scripts
RUN chmod +x ${SRC}/run.sh && \
	chmod +x ${SRC}/scripts/*.sh && \
	chmod +x ${SRC}/scripts/*.py && \
	echo 'alias ls="ls --color=auto"' >> ~/.bashrc

RUN if [ "${build_type}" = "release" ]; then \
	sudo apt-get clean && \
	sudo rm -rf /var/lib/apt/lists/*; \
	fi

ENTRYPOINT ["/bin/bash"]
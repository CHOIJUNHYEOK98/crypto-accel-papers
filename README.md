# GPU 암호 가속 논문 목록

양자내성암호(Post-Quantum Cryptography, PQC)·영지식 증명(Zero-Knowledge Proof, ZKP)·완전 동형암호(Fully Homomorphic Encryption, FHE)를 GPU 에서 구현·최적화한 논문을 출판처별로 모은 목록이다. 앞으로 TPU(Tensor Processing Unit, 구글 AI 가속기)·NPU(Neural Processing Unit, 신경망 처리 장치) 논문도 넣는다.

- 원본 자료: `data/papers.yml`(논문), `data/venues.yml`(출판처), `data/zkp.yml`(ZKP 증명 체계 계열·연산 이름표)
- 페이지: `site/index.html` — 생성기 `build.py` 가 `site/template.html` 틀에 자료를 채워 만든다. **손으로 고치지 않는다.**

## 논문을 더하거나 고치는 법

1. `data/papers.yml` 에 항목을 더한다. 형식은 파일 머리 주석에 있다.

   ```yaml
   - title: 'GZKP: A GPU Accelerated Zero-Knowledge Proof System'
     authors: [Weiliang Ma, Qian Xiong, Xuanhua Shi]
     year: 2023
     venue: asplos          # data/venues.yml 의 id
     field: zkp             # pqc · zkp · fhe · ntt
     device: gpu            # gpu · tpu · npu
     url: https://doi.org/10.1145/3575693.3575711
   ```

   제목에 `:` 가 들어 있으면 작은따옴표로 감싼다.

   ZKP 논문은 세 칸을 더 적는다. 계열과 연산 이름은 `data/zkp.yml` 에 있는 것만 쓰고, 새 계열은 그 파일에 부하 연산 설명·근거와 함께 먼저 더한다.

   ```yaml
     zkp_system: [groth16]          # 증명 체계 계열(여러 체계로 평가했으면 여럿)
     zkp_ops: [msm, ntt, spmv]      # 논문이 가속한 연산
     sys_opt: [resident, overlap, multi-gpu]   # 시스템 관점 최적화(다중 GPU·전송 겹치기 등, 없으면 생략)
     focus: MSM 버킷 모으기를 희소 행렬-벡터 곱으로 바꾼 병렬 MSM   # 핵심 아이디어나 대상 한 줄
   ```
2. 새 출판처면 `data/venues.yml` 에 먼저 더한다. 학회는 [CS 분야 우수 학술대회 목록](https://gist.github.com/Pusnow/6eb933355b5cb8d31ef1abcb3c3e1206)에 실린 곳만 싣고, 그 표의 BK21플러스 IF (2018) 점수(`bk21`)와 한국정보과학회 (2024) 등급(`kiise`)을 적는다. 저널은 점수 칸을 비운다.
3. 페이지를 다시 만든다.

   ```sh
   pip install pyyaml      # 처음 한 번
   python3 build.py        # site/index.html 갱신
   python3 build.py --check
   ```

4. `data/` 와 `site/index.html` 을 함께 커밋하고 끌어오기 요청(Pull Request)을 연다. GitHub Actions 가 `build.py --check` 로 자료 형식과 페이지 최신 여부를 검사하고, `main` 에 합쳐지면 페이지를 다시 게시한다.

## 싣는 기준

- GPU(CUDA·OpenCL·텐서 코어 등) 구현·최적화가 주요 기여인 논문. 응용 시스템 논문 가운데 GPU 구현·평가가 일부로 들어간 것은 `gpu_partial: true`("GPU 평가 포함" 표시).
- FPGA·ASIC 전용 하드웨어 가속기 논문은 싣지 않는다.
- 같은 논문의 예비 공개본과 게재본이 함께 있으면 게재본만 적는다. 게재를 확인하지 못한 ePrint·arXiv 원고는 `venue: preprint`.

## 페이지 보기

https://choijunhyeok98.github.io/crypto-accel-papers/ — `main` 에 올라가면 GitHub Actions 가 검사를 통과한 `site/index.html` 을 GitHub Pages 로 다시 게시한다.

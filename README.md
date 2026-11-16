# GPU 암호 가속 논문 목록

양자내성암호(Post-Quantum Cryptography, PQC)·영지식 증명(Zero-Knowledge Proof, ZKP)·완전 동형암호(Fully Homomorphic Encryption, FHE)를 GPU 에서 구현·최적화한 논문을 출판처별로 모은 목록이다. 앞으로 TPU(Tensor Processing Unit, 구글 AI 가속기)·NPU(Neural Processing Unit, 신경망 처리 장치) 논문도 넣는다.

- 원본 자료: `data/papers.yml`(논문), `data/venues.yml`(출판처)
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
2. 새 출판처면 `data/venues.yml` 에 먼저 더한다. 학회는 [CS 분야 우수 학술대회 목록](https://gist.github.com/Pusnow/6eb933355b5cb8d31ef1abcb3c3e1206)에 실린 곳만 싣고, 그 표의 BK21플러스 IF (2018) 점수(`bk21`)와 한국정보과학회 (2024) 등급(`kiise`)을 적는다. 저널은 점수 칸을 비운다.
3. 페이지를 다시 만든다.

   ```sh
   pip install pyyaml      # 처음 한 번
   python3 build.py        # site/index.html 갱신
   python3 build.py --check
   ```

4. `data/` 와 `site/index.html` 을 함께 커밋하고 끌어오기 요청(Pull Request)을 연다. GitHub Actions 가 `build.py --check` 로 자료 형식과 페이지 최신 여부를 검사한다.

## 싣는 기준

- GPU(CUDA·OpenCL·텐서 코어 등) 구현·최적화가 주요 기여인 논문. 응용 시스템 논문 가운데 GPU 구현·평가가 일부로 들어간 것은 `gpu_partial: true`("GPU 평가 포함" 표시).
- FPGA·ASIC 전용 하드웨어 가속기 논문은 싣지 않는다.
- 같은 논문의 예비 공개본과 게재본이 함께 있으면 게재본만 적는다. 게재를 확인하지 못한 ePrint·arXiv 원고는 `venue: preprint`.

## 페이지 보기

비공개 저장소라 GitHub Pages 는 유료 요금제에서만 켤 수 있다. 저장소의 `site/index.html` 을 내려받아 브라우저로 연다.

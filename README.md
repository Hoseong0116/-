# 숲과나눔 공모전: 장애인콜택시–전기 UD택시 통합 동적운영

이 저장소는 **모델 구현 전 연구환경**이다. 연구의 유일한 기준 문서는 [PROJECT_CONTEXT.md](PROJECT_CONTEXT.md)다.

1. 원본은 `01_raw_data/`에 보존한다.
2. 전처리 결과는 `02_processed_data/`에 Parquet 중심으로 저장한다.
3. 구현은 `04_src/`, 생성 결과는 실행 시 만드는 `06_outputs/`에 둔다.

현재는 학습·시뮬레이션·정책효과 추정을 수행하지 않는다. 자료 상태는 [TODO.md](TODO.md), 변수 정의는 [DATA_DICTIONARY.md](DATA_DICTIONARY.md), 출처는 [SOURCE_MASTER.md](SOURCE_MASTER.md)를 따른다.

팀원과 공유할 데이터의 범위 및 개인정보 제외 원칙은 [DATA_SHARING.md](DATA_SHARING.md), 시뮬레이션 입력 가능 상태와 병합 키는 [모델 입력 안내](02_processed_data/model_inputs/README.md)를 따른다. 수익성 입력 엑셀은 `outputs/profitability_20260918/`에 있다.

# Changelog

## 0.1.0-alpha.20 (2025-07-08)

Full Changelog: [v0.1.0-alpha.19...v0.1.0-alpha.20](https://github.com/mainstay-io/mainstay-python/compare/v0.1.0-alpha.19...v0.1.0-alpha.20)

### Chores

* **internal:** codegen related update ([a4390bf](https://github.com/mainstay-io/mainstay-python/commit/a4390bf779acc04e07a9a07d42e542b06709d93c))

## 0.1.0-alpha.19 (2025-07-02)

Full Changelog: [v0.1.0-alpha.18...v0.1.0-alpha.19](https://github.com/mainstay-io/mainstay-python/compare/v0.1.0-alpha.18...v0.1.0-alpha.19)

### Features

* **api:** api update ([b3bcd7c](https://github.com/mainstay-io/mainstay-python/commit/b3bcd7cde8c40408eff76b2a42610678ebb36a4f))


### Chores

* **ci:** change upload type ([3d16b7d](https://github.com/mainstay-io/mainstay-python/commit/3d16b7d192737538f356d79ef2e5d32d29e39e33))

## 0.1.0-alpha.18 (2025-06-30)

Full Changelog: [v0.1.0-alpha.17...v0.1.0-alpha.18](https://github.com/mainstay-io/mainstay-python/compare/v0.1.0-alpha.17...v0.1.0-alpha.18)

### Bug Fixes

* **ci:** correct conditional ([83c67ed](https://github.com/mainstay-io/mainstay-python/commit/83c67edeb105b6fdc25abc1484e87f8f237f022f))
* **ci:** release-doctor — report correct token name ([68dfc1b](https://github.com/mainstay-io/mainstay-python/commit/68dfc1badb41eaa5335c17a389500d261c03072c))


### Chores

* **ci:** only run for pushes and fork pull requests ([bd9103e](https://github.com/mainstay-io/mainstay-python/commit/bd9103e355a187f37c2837a1a13aaad2eaac30be))

## 0.1.0-alpha.17 (2025-06-24)

Full Changelog: [v0.1.0-alpha.16...v0.1.0-alpha.17](https://github.com/mainstay-io/mainstay-python/compare/v0.1.0-alpha.16...v0.1.0-alpha.17)

### Features

* **client:** add support for aiohttp ([86d9001](https://github.com/mainstay-io/mainstay-python/commit/86d9001f1535459775c68150390ae80ea48772fa))


### Bug Fixes

* **client:** correctly parse binary response | stream ([827f6a3](https://github.com/mainstay-io/mainstay-python/commit/827f6a3d22c87bfb81edb3cc5c0fd7404d90dd11))
* **tests:** fix: tests which call HTTP endpoints directly with the example parameters ([07b67d0](https://github.com/mainstay-io/mainstay-python/commit/07b67d076d3f8ee44c62bda512c45a6135d21b8f))


### Chores

* **ci:** enable for pull requests ([74c97e8](https://github.com/mainstay-io/mainstay-python/commit/74c97e85d982bed75667d5e22a78c78b5f3fee12))
* **internal:** minor formatting ([1844c9e](https://github.com/mainstay-io/mainstay-python/commit/1844c9e0c4f4cb8b59e5dc26479a32030c7948ba))
* **internal:** update conftest.py ([0ad0882](https://github.com/mainstay-io/mainstay-python/commit/0ad08829c03cca7cda4f314c7b9550b79a11f81f))
* **readme:** update badges ([67809de](https://github.com/mainstay-io/mainstay-python/commit/67809dee9565c54f8e85de5d63d9959abd1b7352))
* **tests:** add tests for httpx client instantiation & proxies ([b18e652](https://github.com/mainstay-io/mainstay-python/commit/b18e6520d1ea18a143dcf6d1106e4af234b7c54c))
* **tests:** run tests in parallel ([00a9e6a](https://github.com/mainstay-io/mainstay-python/commit/00a9e6a07fb4d6439373babf1928273a626a6138))
* **tests:** skip some failing tests on the latest python versions ([8c84325](https://github.com/mainstay-io/mainstay-python/commit/8c843255e7100189c49fda1a536b8b3a50a902c1))


### Documentation

* **client:** fix httpx.Timeout documentation reference ([25882d9](https://github.com/mainstay-io/mainstay-python/commit/25882d9d1a6f4a693a60675ee5492b1b060d7753))

## 0.1.0-alpha.16 (2025-06-03)

Full Changelog: [v0.1.0-alpha.15...v0.1.0-alpha.16](https://github.com/mainstay-io/mainstay-python/compare/v0.1.0-alpha.15...v0.1.0-alpha.16)

### Features

* **api:** api update ([1167510](https://github.com/mainstay-io/mainstay-python/commit/1167510cc6cf26442c6b461d2bfbbb55a8c5005a))
* **client:** add follow_redirects request option ([815ff65](https://github.com/mainstay-io/mainstay-python/commit/815ff65bc6bececcee7031357606d15bb254e4c3))


### Bug Fixes

* **package:** support direct resource imports ([07f2cfa](https://github.com/mainstay-io/mainstay-python/commit/07f2cfa6d35618be7629d0cb348e4d664519587a))


### Chores

* **ci:** fix installation instructions ([da62dce](https://github.com/mainstay-io/mainstay-python/commit/da62dce8aa5093d08442a1e0a3dea1abe201f644))
* **ci:** upload sdks to package manager ([2310666](https://github.com/mainstay-io/mainstay-python/commit/23106668161c589cfb32d6ffbfa901734966395a))
* **docs:** grammar improvements ([b68958d](https://github.com/mainstay-io/mainstay-python/commit/b68958d4c95fcbf7591848b0159ed5ab39670c5f))
* **docs:** remove reference to rye shell ([380d8b1](https://github.com/mainstay-io/mainstay-python/commit/380d8b159b7883b7c76af4e86f64252abb592cce))
* **docs:** remove unnecessary param examples ([79f89f2](https://github.com/mainstay-io/mainstay-python/commit/79f89f264ef731c04399dd40339a15e5d9cd04fa))
* **internal:** avoid errors for isinstance checks on proxies ([c347434](https://github.com/mainstay-io/mainstay-python/commit/c34743482227a3da48d87e641031af5088619831))
* **internal:** codegen related update ([70f3a50](https://github.com/mainstay-io/mainstay-python/commit/70f3a50fe903032f97417fb676aa2dd1eb2c4d6c))

## 0.1.0-alpha.15 (2025-04-25)

Full Changelog: [v0.1.0-alpha.14...v0.1.0-alpha.15](https://github.com/mainstay-io/mainstay-python/compare/v0.1.0-alpha.14...v0.1.0-alpha.15)

### Features

* **api:** api update ([0733531](https://github.com/mainstay-io/mainstay-python/commit/0733531485c61204751391787ccd0b381a8d7e74))

## 0.1.0-alpha.14 (2025-04-24)

Full Changelog: [v0.1.0-alpha.13...v0.1.0-alpha.14](https://github.com/mainstay-io/mainstay-python/compare/v0.1.0-alpha.13...v0.1.0-alpha.14)

### Chores

* broadly detect json family of content-type headers ([7ad8eda](https://github.com/mainstay-io/mainstay-python/commit/7ad8eda583f48547cd4aad28c1b3259440a6d91e))
* **ci:** only use depot for staging repos ([5ec85f4](https://github.com/mainstay-io/mainstay-python/commit/5ec85f46c904bb563938920b45984915dc148fca))
* **internal:** codegen related update ([814ba48](https://github.com/mainstay-io/mainstay-python/commit/814ba4800f308e88fcbe432e44bfe05f107d3d74))

## 0.1.0-alpha.13 (2025-04-23)

Full Changelog: [v0.1.0-alpha.12...v0.1.0-alpha.13](https://github.com/mainstay-io/mainstay-python/compare/v0.1.0-alpha.12...v0.1.0-alpha.13)

### Bug Fixes

* **pydantic v1:** more robust ModelField.annotation check ([c687024](https://github.com/mainstay-io/mainstay-python/commit/c6870244b8b82c89409e599ba560778e9f0ea101))


### Chores

* **ci:** add timeout thresholds for CI jobs ([f8efde3](https://github.com/mainstay-io/mainstay-python/commit/f8efde39c03127eedd4056883c46c65d96e93052))
* **internal:** fix list file params ([f8d47b1](https://github.com/mainstay-io/mainstay-python/commit/f8d47b19f7e55bb6a85753157a6b42bf41833639))
* **internal:** import reformatting ([dc4d9d2](https://github.com/mainstay-io/mainstay-python/commit/dc4d9d220a80466bfa98fadfce49916bcf91571c))
* **internal:** refactor retries to not use recursion ([db0a61f](https://github.com/mainstay-io/mainstay-python/commit/db0a61fe4dd574508de74ffd9ecf2c0e8b437b6b))

## 0.1.0-alpha.12 (2025-04-19)

Full Changelog: [v0.1.0-alpha.11...v0.1.0-alpha.12](https://github.com/mainstay-io/mainstay-python/compare/v0.1.0-alpha.11...v0.1.0-alpha.12)

### Chores

* **internal:** update models test ([3ee54b0](https://github.com/mainstay-io/mainstay-python/commit/3ee54b06842d118c496b626f36802d4ada9c2487))

## 0.1.0-alpha.11 (2025-04-17)

Full Changelog: [v0.1.0-alpha.10...v0.1.0-alpha.11](https://github.com/mainstay-io/mainstay-python/compare/v0.1.0-alpha.10...v0.1.0-alpha.11)

### Chores

* **internal:** base client updates ([957c83a](https://github.com/mainstay-io/mainstay-python/commit/957c83ac75f285862e25fc706be39d641d9f5340))
* **internal:** bump pyright version ([b8838df](https://github.com/mainstay-io/mainstay-python/commit/b8838df171b57d4fb9acdb50d0f06714136a0915))

## 0.1.0-alpha.10 (2025-04-15)

Full Changelog: [v0.1.0-alpha.9...v0.1.0-alpha.10](https://github.com/mainstay-io/mainstay-python/compare/v0.1.0-alpha.9...v0.1.0-alpha.10)

### Chores

* **client:** minor internal fixes ([b6e1603](https://github.com/mainstay-io/mainstay-python/commit/b6e1603ef847b3fb260faea2743153205ff5f06d))
* **internal:** update pyright settings ([ff3d380](https://github.com/mainstay-io/mainstay-python/commit/ff3d380df5889009f5fa3ef8d58de58baa607543))


### Documentation

* remove private imports from datetime snippets ([8aa900f](https://github.com/mainstay-io/mainstay-python/commit/8aa900f0eb1a5780d6cf9b2334d791821ebb5adb))

## 0.1.0-alpha.9 (2025-04-12)

Full Changelog: [v0.1.0-alpha.8...v0.1.0-alpha.9](https://github.com/mainstay-io/mainstay-python/compare/v0.1.0-alpha.8...v0.1.0-alpha.9)

### Bug Fixes

* **perf:** optimize some hot paths ([24aa4f5](https://github.com/mainstay-io/mainstay-python/commit/24aa4f5fc18c0a3c04b3118299f403417e2bbb3c))
* **perf:** skip traversing types for NotGiven values ([d89010c](https://github.com/mainstay-io/mainstay-python/commit/d89010c9bb21e6ce9c0d32dea289daaf576f9a10))

## 0.1.0-alpha.8 (2025-04-10)

Full Changelog: [v0.1.0-alpha.7...v0.1.0-alpha.8](https://github.com/mainstay-io/mainstay-python/compare/v0.1.0-alpha.7...v0.1.0-alpha.8)

### Chores

* **internal:** expand CI branch coverage ([81d5960](https://github.com/mainstay-io/mainstay-python/commit/81d596067eb6633c966ecab54c3ad357adbea56f))
* **internal:** reduce CI branch coverage ([3d4ba44](https://github.com/mainstay-io/mainstay-python/commit/3d4ba44231272b3a9336e53a6390ea7e076b8480))

## 0.1.0-alpha.7 (2025-04-09)

Full Changelog: [v0.1.0-alpha.6...v0.1.0-alpha.7](https://github.com/mainstay-io/mainstay-python/compare/v0.1.0-alpha.6...v0.1.0-alpha.7)

### Chores

* **internal:** only run examples workflow in main repo ([#110](https://github.com/mainstay-io/mainstay-python/issues/110)) ([2b1ecd4](https://github.com/mainstay-io/mainstay-python/commit/2b1ecd42b51388c703e178fb1a50657e9d681227))
* **internal:** remove trailing character ([#109](https://github.com/mainstay-io/mainstay-python/issues/109)) ([bbcc519](https://github.com/mainstay-io/mainstay-python/commit/bbcc51963d6de70d2dc3bf2cc244451c6d570a85))
* **internal:** slight transform perf improvement ([#111](https://github.com/mainstay-io/mainstay-python/issues/111)) ([c995c02](https://github.com/mainstay-io/mainstay-python/commit/c995c02bdbee359299f72e7d70b4fd22f5210483))

## 0.1.0-alpha.6 (2025-03-27)

Full Changelog: [v0.1.0-alpha.5...v0.1.0-alpha.6](https://github.com/mainstay-io/mainstay-python/compare/v0.1.0-alpha.5...v0.1.0-alpha.6)

### Features

* **api:** api update ([#69](https://github.com/mainstay-io/mainstay-python/issues/69)) ([c1af6f4](https://github.com/mainstay-io/mainstay-python/commit/c1af6f4e35c77c99fcdbfc576ed5168333e5da4a))
* **api:** api update ([#91](https://github.com/mainstay-io/mainstay-python/issues/91)) ([4efb101](https://github.com/mainstay-io/mainstay-python/commit/4efb10138105118ae7e2f9d28824b7f2ebdff334))
* **api:** api update ([#92](https://github.com/mainstay-io/mainstay-python/issues/92)) ([f4e69e8](https://github.com/mainstay-io/mainstay-python/commit/f4e69e8d60160cbb38497656a746cbfb9c99de50))
* **client:** allow passing `NotGiven` for body ([#90](https://github.com/mainstay-io/mainstay-python/issues/90)) ([f80fb7b](https://github.com/mainstay-io/mainstay-python/commit/f80fb7bcc90ec1f001b1740de4f4aa3414ec83f8))
* **client:** send `X-Stainless-Read-Timeout` header ([#84](https://github.com/mainstay-io/mainstay-python/issues/84)) ([7196478](https://github.com/mainstay-io/mainstay-python/commit/7196478404b1cb2a315bd04b8be4a4dc4fb4f8a2))


### Bug Fixes

* asyncify on non-asyncio runtimes ([#89](https://github.com/mainstay-io/mainstay-python/issues/89)) ([ef000b1](https://github.com/mainstay-io/mainstay-python/commit/ef000b1fd52c20da346f91f88240dcc9de405f19))
* **ci:** ensure pip is always available ([#104](https://github.com/mainstay-io/mainstay-python/issues/104)) ([fa83b23](https://github.com/mainstay-io/mainstay-python/commit/fa83b23a9ae7e2ff611cbcd0759fa17028d7276a))
* **ci:** remove publishing patch ([#105](https://github.com/mainstay-io/mainstay-python/issues/105)) ([29488e7](https://github.com/mainstay-io/mainstay-python/commit/29488e7817874b6fcfa8c1a05770b0e067f4e1a8))
* **client:** mark some request bodies as optional ([f80fb7b](https://github.com/mainstay-io/mainstay-python/commit/f80fb7bcc90ec1f001b1740de4f4aa3414ec83f8))
* **client:** only call .close() when needed ([#72](https://github.com/mainstay-io/mainstay-python/issues/72)) ([973001b](https://github.com/mainstay-io/mainstay-python/commit/973001b6faa172f336e8d8f0986a6de3eaae174d))
* correctly handle deserialising `cls` fields ([#75](https://github.com/mainstay-io/mainstay-python/issues/75)) ([1559434](https://github.com/mainstay-io/mainstay-python/commit/1559434d3ebf102a8df17cd72962ca22deb8ddc6))
* **tests:** make test_get_platform less flaky ([#78](https://github.com/mainstay-io/mainstay-python/issues/78)) ([a331e1e](https://github.com/mainstay-io/mainstay-python/commit/a331e1e0cc1678525d8cb05a95ab6ed4614483ab))
* **types:** handle more discriminated union shapes ([#103](https://github.com/mainstay-io/mainstay-python/issues/103)) ([8fbaa8e](https://github.com/mainstay-io/mainstay-python/commit/8fbaa8e5ffb287a9abb8aa02f76622f9aaf7f070))


### Chores

* add missing isclass check ([#70](https://github.com/mainstay-io/mainstay-python/issues/70)) ([a1f4d8d](https://github.com/mainstay-io/mainstay-python/commit/a1f4d8d0e754afe9aab8fac411f57faae086ed55))
* **docs:** update client docstring ([#96](https://github.com/mainstay-io/mainstay-python/issues/96)) ([27ad79c](https://github.com/mainstay-io/mainstay-python/commit/27ad79ca6d09986f45769d7ce9009dcb2a7b8c61))
* fix typos ([#106](https://github.com/mainstay-io/mainstay-python/issues/106)) ([d95475d](https://github.com/mainstay-io/mainstay-python/commit/d95475d9d0fa074d7ee47242866450c30b05956f))
* **internal:** avoid pytest-asyncio deprecation warning ([#79](https://github.com/mainstay-io/mainstay-python/issues/79)) ([d1da494](https://github.com/mainstay-io/mainstay-python/commit/d1da494fa5d4b4c7817e52e4f7de57ff090b4f1b))
* **internal:** bummp ruff dependency ([#83](https://github.com/mainstay-io/mainstay-python/issues/83)) ([ebe609e](https://github.com/mainstay-io/mainstay-python/commit/ebe609e9a7b601a905cad57a2842a5d76196eba3))
* **internal:** bump httpx dependency ([#71](https://github.com/mainstay-io/mainstay-python/issues/71)) ([8f41c01](https://github.com/mainstay-io/mainstay-python/commit/8f41c019af13a440151a0d9e438723ae092b35e8))
* **internal:** bump rye to 0.44.0 ([#102](https://github.com/mainstay-io/mainstay-python/issues/102)) ([3af2d61](https://github.com/mainstay-io/mainstay-python/commit/3af2d61a40db1ee4b3674a11492509c42c99cbd7))
* **internal:** change default timeout to an int ([#82](https://github.com/mainstay-io/mainstay-python/issues/82)) ([0075d58](https://github.com/mainstay-io/mainstay-python/commit/0075d58f8be38a573fb2c85d0fedb5feb89e0583))
* **internal:** codegen related update ([#101](https://github.com/mainstay-io/mainstay-python/issues/101)) ([bbf3e77](https://github.com/mainstay-io/mainstay-python/commit/bbf3e7739c7623c5ba19833842b11a07577002e1))
* **internal:** codegen related update ([#65](https://github.com/mainstay-io/mainstay-python/issues/65)) ([03f1f2a](https://github.com/mainstay-io/mainstay-python/commit/03f1f2a886be071f4b2eb125edebdf02905975f5))
* **internal:** codegen related update ([#68](https://github.com/mainstay-io/mainstay-python/issues/68)) ([d970ae4](https://github.com/mainstay-io/mainstay-python/commit/d970ae41269c1fd5606e32135c32d8be0b88b6d4))
* **internal:** codegen related update ([#74](https://github.com/mainstay-io/mainstay-python/issues/74)) ([82d61d8](https://github.com/mainstay-io/mainstay-python/commit/82d61d8f408c7bf692905f84e3b77a2628b2f2bd))
* **internal:** codegen related update ([#76](https://github.com/mainstay-io/mainstay-python/issues/76)) ([6ec5b58](https://github.com/mainstay-io/mainstay-python/commit/6ec5b58fed5915282f2a0ccfc0d9112bcad5a973))
* **internal:** fix devcontainers setup ([#93](https://github.com/mainstay-io/mainstay-python/issues/93)) ([69931e7](https://github.com/mainstay-io/mainstay-python/commit/69931e774efb4cf1b0819deb9826fc3aed39dd3e))
* **internal:** fix some typos ([#67](https://github.com/mainstay-io/mainstay-python/issues/67)) ([79048df](https://github.com/mainstay-io/mainstay-python/commit/79048df735a4e45f556ad0d133b701324250bcbd))
* **internal:** fix type traversing dictionary params ([#85](https://github.com/mainstay-io/mainstay-python/issues/85)) ([04243eb](https://github.com/mainstay-io/mainstay-python/commit/04243ebea0e9bdc0aa3250f1638f26c229d4d113))
* **internal:** minor formatting changes ([#81](https://github.com/mainstay-io/mainstay-python/issues/81)) ([56dfae7](https://github.com/mainstay-io/mainstay-python/commit/56dfae7570cba9b16943153be17ceb75a718660b))
* **internal:** minor style changes ([#80](https://github.com/mainstay-io/mainstay-python/issues/80)) ([3e7cff0](https://github.com/mainstay-io/mainstay-python/commit/3e7cff042d18439c479057617944a26915efb06d))
* **internal:** minor type handling changes ([#87](https://github.com/mainstay-io/mainstay-python/issues/87)) ([22c603e](https://github.com/mainstay-io/mainstay-python/commit/22c603e9c2ebbd3d461bf3c970fa58ffaf31f465))
* **internal:** properly set __pydantic_private__ ([#94](https://github.com/mainstay-io/mainstay-python/issues/94)) ([de410ee](https://github.com/mainstay-io/mainstay-python/commit/de410ee037706851f2a84b541cc47822d4b34cb3))
* **internal:** remove extra empty newlines ([#100](https://github.com/mainstay-io/mainstay-python/issues/100)) ([66e3b44](https://github.com/mainstay-io/mainstay-python/commit/66e3b44203cf0bc2cbf88e8ab9064250311a00a7))
* **internal:** remove unused http client options forwarding ([#97](https://github.com/mainstay-io/mainstay-python/issues/97)) ([2244efb](https://github.com/mainstay-io/mainstay-python/commit/2244efb766f81bdabdb6c7a599374eff75d244a3))
* **internal:** update client tests ([#88](https://github.com/mainstay-io/mainstay-python/issues/88)) ([fc28a34](https://github.com/mainstay-io/mainstay-python/commit/fc28a3487a7b7003f93b050726e93e0f1b0bca47))


### Documentation

* fix typos ([#73](https://github.com/mainstay-io/mainstay-python/issues/73)) ([df20009](https://github.com/mainstay-io/mainstay-python/commit/df20009958a6cdde153733510d7dba05e28a2a1d))
* **raw responses:** fix duplicate `the` ([#77](https://github.com/mainstay-io/mainstay-python/issues/77)) ([a485969](https://github.com/mainstay-io/mainstay-python/commit/a4859694d237df8e9ca254c178bcd2aca7f571f9))
* revise readme docs about nested params ([#98](https://github.com/mainstay-io/mainstay-python/issues/98)) ([1510997](https://github.com/mainstay-io/mainstay-python/commit/1510997e8a2b019e350e4366e3a1beb0187d6b1b))
* update URLs from stainlessapi.com to stainless.com ([#95](https://github.com/mainstay-io/mainstay-python/issues/95)) ([4085a58](https://github.com/mainstay-io/mainstay-python/commit/4085a587ee71f7a80436fd0660c115a91c271802))

## 0.1.0-alpha.5 (2024-12-17)

Full Changelog: [v0.1.0-alpha.4...v0.1.0-alpha.5](https://github.com/mainstay-io/mainstay-python/compare/v0.1.0-alpha.4...v0.1.0-alpha.5)

### Features

* **api:** api update ([#40](https://github.com/mainstay-io/mainstay-python/issues/40)) ([36667ac](https://github.com/mainstay-io/mainstay-python/commit/36667ac08944c80aba5cc8d7c72d7d7f0ea1a004))
* **api:** api update ([#41](https://github.com/mainstay-io/mainstay-python/issues/41)) ([fd6f8cd](https://github.com/mainstay-io/mainstay-python/commit/fd6f8cd10606dcc2949a1cd28a2293c1da1fca65))
* **api:** api update ([#63](https://github.com/mainstay-io/mainstay-python/issues/63)) ([6be4a1a](https://github.com/mainstay-io/mainstay-python/commit/6be4a1ad08bf87054328ea028a1454c605172156))
* **api:** OpenAPI spec update via Stainless API ([#22](https://github.com/mainstay-io/mainstay-python/issues/22)) ([f4716c8](https://github.com/mainstay-io/mainstay-python/commit/f4716c853a3f0801b87f68aea93569fd12c9e900))
* **api:** OpenAPI spec update via Stainless API ([#24](https://github.com/mainstay-io/mainstay-python/issues/24)) ([3b6b609](https://github.com/mainstay-io/mainstay-python/commit/3b6b609e57956768eedb7bb87835ea03d8f0dcf8))


### Bug Fixes

* **client:** avoid OverflowError with very large retry counts ([#38](https://github.com/mainstay-io/mainstay-python/issues/38)) ([2a79dc1](https://github.com/mainstay-io/mainstay-python/commit/2a79dc1b5dbde0734d20e5e19d862631be31dbd8))
* **client:** compat with new httpx 0.28.0 release ([#56](https://github.com/mainstay-io/mainstay-python/issues/56)) ([b0ef1bb](https://github.com/mainstay-io/mainstay-python/commit/b0ef1bb571af61399dac2033853c39af6f7cdf87))


### Chores

* add docstrings to raw response properties ([#29](https://github.com/mainstay-io/mainstay-python/issues/29)) ([8bade40](https://github.com/mainstay-io/mainstay-python/commit/8bade405417f0b65117dc140f23b51016e46a162))
* add repr to PageInfo class ([#39](https://github.com/mainstay-io/mainstay-python/issues/39)) ([e4b6d4b](https://github.com/mainstay-io/mainstay-python/commit/e4b6d4b996ab0c7cc1ae172f450b4bb7bc3e25c8))
* **ci:** also run pydantic v1 tests ([#26](https://github.com/mainstay-io/mainstay-python/issues/26)) ([07d20ff](https://github.com/mainstay-io/mainstay-python/commit/07d20fffc6228f2502eccba21ee281ab95541b68))
* **client:** fix parsing union responses when non-json is returned ([#25](https://github.com/mainstay-io/mainstay-python/issues/25)) ([c996d8c](https://github.com/mainstay-io/mainstay-python/commit/c996d8c026679e3c20ad9ae6902c02895043e3f4))
* **internal:** add support for parsing bool response content ([#37](https://github.com/mainstay-io/mainstay-python/issues/37)) ([a660ad9](https://github.com/mainstay-io/mainstay-python/commit/a660ad9619804d52f03a7e2e248e7cfdb6ab08b9))
* **internal:** add support for TypeAliasType ([#62](https://github.com/mainstay-io/mainstay-python/issues/62)) ([83038e7](https://github.com/mainstay-io/mainstay-python/commit/83038e7b7dfb13a121574eb6aed24c4e326833c7))
* **internal:** bump pydantic dependency ([#59](https://github.com/mainstay-io/mainstay-python/issues/59)) ([08f4883](https://github.com/mainstay-io/mainstay-python/commit/08f48839910fba704386c2c5cd7a43f3342b2bcf))
* **internal:** bump pyright ([#57](https://github.com/mainstay-io/mainstay-python/issues/57)) ([bf998ca](https://github.com/mainstay-io/mainstay-python/commit/bf998ca41db02b9bd7419518028a427b0b3cc660))
* **internal:** bump pyright ([#61](https://github.com/mainstay-io/mainstay-python/issues/61)) ([aa9fd58](https://github.com/mainstay-io/mainstay-python/commit/aa9fd58da6f5fad55510593b894e2ff85872ebe1))
* **internal:** bump pyright / mypy version ([#33](https://github.com/mainstay-io/mainstay-python/issues/33)) ([5ecd312](https://github.com/mainstay-io/mainstay-python/commit/5ecd31253e2ec9bf285ecd487cf0d707bfbdd4d3))
* **internal:** bump ruff ([#32](https://github.com/mainstay-io/mainstay-python/issues/32)) ([c714557](https://github.com/mainstay-io/mainstay-python/commit/c714557340bd5ab1dd3adaef3e9740209a6706ef))
* **internal:** codegen related update ([#31](https://github.com/mainstay-io/mainstay-python/issues/31)) ([e320a0b](https://github.com/mainstay-io/mainstay-python/commit/e320a0ba20616acfe1e52d69add23a6606d29943))
* **internal:** codegen related update ([#34](https://github.com/mainstay-io/mainstay-python/issues/34)) ([115e9df](https://github.com/mainstay-io/mainstay-python/commit/115e9dffaf1919803d4dae06ee715329c9b82b9e))
* **internal:** codegen related update ([#35](https://github.com/mainstay-io/mainstay-python/issues/35)) ([9aad407](https://github.com/mainstay-io/mainstay-python/commit/9aad4072a08d06709d2ca92e322726591c46bbc9))
* **internal:** codegen related update ([#36](https://github.com/mainstay-io/mainstay-python/issues/36)) ([e778d96](https://github.com/mainstay-io/mainstay-python/commit/e778d96c9344e30d26e58f4390dd60a4f1701d4c))
* **internal:** codegen related update ([#54](https://github.com/mainstay-io/mainstay-python/issues/54)) ([8d3e441](https://github.com/mainstay-io/mainstay-python/commit/8d3e4419ef6fb66347dc86cc637b6bc66c4bc074))
* **internal:** codegen related update ([#55](https://github.com/mainstay-io/mainstay-python/issues/55)) ([827fd58](https://github.com/mainstay-io/mainstay-python/commit/827fd58fd65ca60f44d9429f36113809be347255))
* **internal:** fix compat model_dump method when warnings are passed ([#52](https://github.com/mainstay-io/mainstay-python/issues/52)) ([87753e1](https://github.com/mainstay-io/mainstay-python/commit/87753e1f7694ff135fe0d3eab01a5e7daeb0d5a1))
* **internal:** use different 32bit detection method ([#23](https://github.com/mainstay-io/mainstay-python/issues/23)) ([2543e59](https://github.com/mainstay-io/mainstay-python/commit/2543e592fe2f010300ec627f3546136868f9de98))
* **internal:** version bump ([#20](https://github.com/mainstay-io/mainstay-python/issues/20)) ([2f51381](https://github.com/mainstay-io/mainstay-python/commit/2f513815237ee8eb057b8ef07b3f4ebfb69d3724))
* make the `Omit` type public ([#58](https://github.com/mainstay-io/mainstay-python/issues/58)) ([91aa7ae](https://github.com/mainstay-io/mainstay-python/commit/91aa7aeb76c5f608a58760a58876d3f758351f95))
* pyproject.toml formatting changes ([#28](https://github.com/mainstay-io/mainstay-python/issues/28)) ([70d893a](https://github.com/mainstay-io/mainstay-python/commit/70d893a160d73267060b17bc06effd2f6462cdd8))
* rebuild project due to codegen change ([#42](https://github.com/mainstay-io/mainstay-python/issues/42)) ([74f0a29](https://github.com/mainstay-io/mainstay-python/commit/74f0a298393faf292a3ff00755e1931e19f175f7))
* rebuild project due to codegen change ([#43](https://github.com/mainstay-io/mainstay-python/issues/43)) ([987ace3](https://github.com/mainstay-io/mainstay-python/commit/987ace3ab6c9b30f71fae2b0440b8e314ef3403c))
* rebuild project due to codegen change ([#44](https://github.com/mainstay-io/mainstay-python/issues/44)) ([e15f71d](https://github.com/mainstay-io/mainstay-python/commit/e15f71da1298975ca773b434a1533b01891b2a14))
* rebuild project due to codegen change ([#45](https://github.com/mainstay-io/mainstay-python/issues/45)) ([d2c7122](https://github.com/mainstay-io/mainstay-python/commit/d2c7122a0cf138cf2deac02dc176c921441f4008))
* rebuild project due to codegen change ([#46](https://github.com/mainstay-io/mainstay-python/issues/46)) ([e990905](https://github.com/mainstay-io/mainstay-python/commit/e9909050731b4598baa7a81a0c93905d6353542e))
* rebuild project due to codegen change ([#47](https://github.com/mainstay-io/mainstay-python/issues/47)) ([d6ab7b4](https://github.com/mainstay-io/mainstay-python/commit/d6ab7b40f8316fc13f52246c9a3df78665733e6c))
* rebuild project due to codegen change ([#48](https://github.com/mainstay-io/mainstay-python/issues/48)) ([21a91a4](https://github.com/mainstay-io/mainstay-python/commit/21a91a4f545dfc41895642f7df359fca1b47d5ed))
* rebuild project due to codegen change ([#49](https://github.com/mainstay-io/mainstay-python/issues/49)) ([6a9fe31](https://github.com/mainstay-io/mainstay-python/commit/6a9fe317d9c68f88e4a4e907916fba52bbac9059))
* rebuild project due to codegen change ([#50](https://github.com/mainstay-io/mainstay-python/issues/50)) ([fc4ea9e](https://github.com/mainstay-io/mainstay-python/commit/fc4ea9e2bf6eeaff9886ba5b82dbf7a5f599be9a))
* rebuild project due to codegen change ([#51](https://github.com/mainstay-io/mainstay-python/issues/51)) ([12db39a](https://github.com/mainstay-io/mainstay-python/commit/12db39a1c3947a4ccf847640b1da7a8dcc849f72))


### Documentation

* add info log level to readme ([#53](https://github.com/mainstay-io/mainstay-python/issues/53)) ([d481c14](https://github.com/mainstay-io/mainstay-python/commit/d481c1483c37675278f4b1ef678f72e5117bca16))
* **readme:** add section on determining installed version ([#30](https://github.com/mainstay-io/mainstay-python/issues/30)) ([1841ede](https://github.com/mainstay-io/mainstay-python/commit/1841edecdb4958bf0cb4d3c34b23bf6b09a08a14))
* **readme:** fix http client proxies example ([#60](https://github.com/mainstay-io/mainstay-python/issues/60)) ([69bfe9d](https://github.com/mainstay-io/mainstay-python/commit/69bfe9d6e77b0ad38676deeec95ac864d8135658))

## 0.1.0-alpha.4 (2024-08-14)

Full Changelog: [v0.1.0-alpha.3...v0.1.0-alpha.4](https://github.com/mainstay-io/mainstay-python/compare/v0.1.0-alpha.3...v0.1.0-alpha.4)

### Features

* add parallelized calls code ([91f3c4c](https://github.com/mainstay-io/mainstay-python/commit/91f3c4cdd62befe8f1407e7fc0171540fede450e))
* added crime and school parallelized calls ([7edfa2e](https://github.com/mainstay-io/mainstay-python/commit/7edfa2eec3556edb72f85fa36742c37b17cd4a72))
* clean up on top of the diffs + questions ([ebef7e7](https://github.com/mainstay-io/mainstay-python/commit/ebef7e7b65092f6bd7b6932428ac65b44b1b60e4))
* copied changes ([76364b7](https://github.com/mainstay-io/mainstay-python/commit/76364b79a730c71eb119551c445fd92516a62edf))
* fix imports ([1165409](https://github.com/mainstay-io/mainstay-python/commit/11654099fb2e5c0eccd4f37c3dc10f2b763eb6c9))
* fix names ([f96c489](https://github.com/mainstay-io/mainstay-python/commit/f96c489241b9e1c4da39a33b6bfa4082a71382de))
* fixed examples files linting ([26c4a60](https://github.com/mainstay-io/mainstay-python/commit/26c4a60deabe2bb7b5a621199ed6a7c97167875d))
* revert all the accidental custom codes, keep only the parallelized calls ([bb045b7](https://github.com/mainstay-io/mainstay-python/commit/bb045b7770017fb08891845a436c826e5f9310f5))

## 0.1.0-alpha.3 (2024-08-13)

Full Changelog: [v0.1.0-alpha.2...v0.1.0-alpha.3](https://github.com/mainstay-io/mainstay-python/compare/v0.1.0-alpha.2...v0.1.0-alpha.3)

### Features

* **api:** manual updates ([#15](https://github.com/mainstay-io/mainstay-python/issues/15)) ([6b3e125](https://github.com/mainstay-io/mainstay-python/commit/6b3e125658144d4f687bb9ccfa6dd9eedaa57624))
* **api:** OpenAPI spec update via Stainless API ([#16](https://github.com/mainstay-io/mainstay-python/issues/16)) ([8a2263a](https://github.com/mainstay-io/mainstay-python/commit/8a2263a1b99f3dc3cde7c96a64ea1f6da9273ce3))


### Chores

* **examples:** minor formatting changes ([#10](https://github.com/mainstay-io/mainstay-python/issues/10)) ([ccf2d18](https://github.com/mainstay-io/mainstay-python/commit/ccf2d18a1c89a3dd1e2104de4e9a1a5ddefcd888))
* **internal:** codegen related update ([#13](https://github.com/mainstay-io/mainstay-python/issues/13)) ([69c2224](https://github.com/mainstay-io/mainstay-python/commit/69c222485cc5a0580b51b13609f8a503e8bfb5e9))
* **internal:** version bump ([#11](https://github.com/mainstay-io/mainstay-python/issues/11)) ([b584ac1](https://github.com/mainstay-io/mainstay-python/commit/b584ac161dc6915e58e6fc161e06604985c1ad40))

## 0.1.0-alpha.2 (2024-08-10)

Full Changelog: [v0.1.0-alpha.1...v0.1.0-alpha.2](https://github.com/mainstay-io/mainstay-python/compare/v0.1.0-alpha.1...v0.1.0-alpha.2)

### Chores

* **ci:** bump prism mock server version ([#6](https://github.com/mainstay-io/mainstay-python/issues/6)) ([1f9d7f8](https://github.com/mainstay-io/mainstay-python/commit/1f9d7f817d34419f9603c25f1206678706db5e57))
* **internal:** ensure package is importable in lint cmd ([#8](https://github.com/mainstay-io/mainstay-python/issues/8)) ([c49ec2b](https://github.com/mainstay-io/mainstay-python/commit/c49ec2b58d18671eaea432058367f95645ec3d39))

## 0.1.0-alpha.1 (2024-08-10)

Full Changelog: [v0.0.1-alpha.0...v0.1.0-alpha.1](https://github.com/mainstay-io/mainstay-python/compare/v0.0.1-alpha.0...v0.1.0-alpha.1)

### Features

* **api:** OpenAPI spec update via Stainless API ([9cd559e](https://github.com/mainstay-io/mainstay-python/commit/9cd559e96e2d154346a17d225bdea3a3ad3d78b6))
* **api:** OpenAPI spec update via Stainless API ([ab54c3c](https://github.com/mainstay-io/mainstay-python/commit/ab54c3c0b590cd2197359984da5242bfebe2ebe8))


### Chores

* go live ([#2](https://github.com/mainstay-io/mainstay-python/issues/2)) ([e8fb3e5](https://github.com/mainstay-io/mainstay-python/commit/e8fb3e5bc68c7b4fc331e9ac9fba91d7a8bf0120))

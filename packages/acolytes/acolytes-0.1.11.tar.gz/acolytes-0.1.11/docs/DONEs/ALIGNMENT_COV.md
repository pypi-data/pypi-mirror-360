| Name | Stmts | Miss | Cover | Missing |
| :--- | :--- | :--- | :--- | :--- |
| `src\acolyte\__init__.py` | 4 | 0 | 100% | |
| `src\acolyte\__main__.py` | 2 | 2 | 0% | 17-20 |
| `src\acolyte\api\__init__.py` | 98 | 2 | 98% | 87-88 |
| `src\acolyte\api\dream.py` | 136 | 0 | 100% | |
| `src\acolyte\api\health.py` | 261 | 22 | 92% | 49, 62, 432-433, 445-457, 479-481, 516-517, 566, 646-648 |
| `src\acolyte\api\index.py` | 224 | 22 | 90% | 119, 127-129, 234-236, 276-283, 354-355, 405-416, 479-480, 546-548 |
| `src\acolyte\api\openai.py` | 173 | 5 | 97% | 93, 126, 422, 437-438 |
| `src\acolyte\api\websockets\__init__.py` | 3 | 0 | 100% | |
| `src\acolyte\api\websockets\progress.py` | 136 | 7 | 95% | 53, 59, 65, 272-273, 275-276 |
| `src\acolyte\core\__init__.py` | 16 | 0 | 100% | |
| `src\acolyte\core\chunking_config.py` | 62 | 0 | 100% | |
| `src\acolyte\core\database.py` | 159 | 0 | 100% | |
| `src\acolyte\core\database_schemas\__init__.py`| 2 | 0 | 100% | |
| `src\acolyte\core\events.py` | 184 | 1 | 99% | 410 |
| `src\acolyte\core\exceptions.py` | 104 | 0 | 100% | |
| `src\acolyte\core\id_generator.py` | 65 | 0 | 100% | |
| `src\acolyte\core\logging.py` | 67 | 0 | 100% | |
| `src\acolyte\core\ollama.py` | 124 | 6 | 95% | 136, 162, 192, 197, 245, 293 |
| `src\acolyte\core\secure_config.py` | 89 | 0 | 100% | |
| `src\acolyte\core\token_counter.py` | 247 | 13 | 95% | 158, 347, 362-373, 511, 563-565 |
| `src\acolyte\core\tracing.py` | 31 | 0 | 100% | |
| `src\acolyte\dream\__init__.py` | 24 | 4 | 83% | 24-26, 44 |
| `src\acolyte\dream\analyzer.py` | 434 | 22 | 95% | 460-461, 510, 519-521, 535-537, 620-621, 660-661, 763, 780-781, 786-789, 958-959 |
| `src\acolyte\dream\fatigue_monitor.py` | 266 | 11 | 96% | 165, 294-296, 338, 343-345, 437-439 |
| `src\acolyte\dream\insight_writer.py` | 384 | 0 | 100% | |
| `src\acolyte\dream\orchestrator.py` | 236 | 10 | 96% | 269, 537-538, 648-649, 680-681, 685-689 |
| `src\acolyte\dream\prompts\__init__.py` | 0 | 0 | 100% | |
| `src\acolyte\dream\state_manager.py` | 190 | 10 | 95% | 118-120, 142-143, 192, 243, 358, 479-480 |
| `src\acolyte\embeddings\__init__.py` | 50 | 0 | 100% | |
| `src\acolyte\embeddings\cache.py` | 80 | 2 | 98% | 165-166 |
| `src\acolyte\embeddings\context.py` | 64 | 0 | 100% | |
| `src\acolyte\embeddings\metrics.py` | 215 | 1 | 99% | 164 |
| `src\acolyte\embeddings\persistent_cache.py`| 130 | 1 | 99% | 58 |
| `src\acolyte\embeddings\reranker.py` | 153 | 4 | 97% | 90, 160, 162, 354 |
| `src\acolyte\embeddings\types.py` | 65 | 5 | 92% | 170, 174, 178, 182, 186 |
| `src\acolyte\embeddings\unixcoder.py` | 395 | 54 | 86% | 194, 263-270, 312, 318, 401-414, 427-428, 478, 547-596, 716 |
| `src\acolyte\models\__init__.py` | 12 | 0 | 100% | |
| `src\acolyte\models\base.py` | 39 | 0 | 100% | |
| `src\acolyte\models\chat.py` | 51 | 0 | 100% | |
| `src\acolyte\models\chunk.py` | 55 | 0 | 100% | |
| `src\acolyte\models\common\__init__.py` | 2 | 0 | 100% | |
| `src\acolyte\models\common\metadata.py` | 45 | 0 | 100% | |
| `src\acolyte\models\conversation.py` | 51 | 0 | 100% | |
| `src\acolyte\models\document.py` | 77 | 0 | 100% | |
| `src\acolyte\models\dream.py` | 67 | 0 | 100% | |
| `src\acolyte\models\semantic_types.py` | 32 | 0 | 100% | |
| `src\acolyte\models\task_checkpoint.py` | 46 | 0 | 100% | |
| `src\acolyte\models\technical_decision.py` | 33 | 0 | 100% | |
| `src\acolyte\rag\__init__.py` | 3 | 0 | 100% | |
| `src\acolyte\rag\chunking\__init__.py` | 3 | 0 | 100% | |
| `src\acolyte\rag\chunking\adaptive.py` | 113 | 0 | 100% | |
| `src\acolyte\rag\chunking\base.py` | 309 | 15 | 95% | 260-262, 365, 385-386, 389-395, 528, 611-612 |
| `src\acolyte\rag\chunking\factory.py` | 105 | 2 | 98% | 223-224 |
| `src\acolyte\rag\chunking\language_config.py`| 1 | 0 | 100% | |
| `src\acolyte\rag\chunking\language_mappings.py`| 15 | 0 | 100% | |
| `src\acolyte\rag\chunking\languages\__init__.py`| 108 | 0 | 100% | |
| `src\acolyte\rag\chunking\languages\bash.py` | 107 | 6 | 94% | 34, 38, 110, 156, 198, 235 |
| `src\acolyte\rag\chunking\languages\c.py` | 204 | 3 | 99% | 41, 108, 166 |
| `src\acolyte\rag\chunking\languages\config_base.py`| 174 | 4 | 98% | 37, 288, 356-357 |
| `src\acolyte\rag\chunking\languages\cpp.py` | 495 | 55 | 89% | 101, 282-283, 345-350, 360, 419-422, 454-456, 460, 578, 642, 742, 788, 796, 801, 812-813, 817, 833, 851-870, 892-893, 943-948, 967, 981, 1041-1048, 1076 |
| `src\acolyte\rag\chunking\languages\csharp.py`| 259 | 14 | 95% | 61, 65, 69, 436, 438, 443, 469, 473, 476, 480, 530, 562, 606-614 |
| `src\acolyte\rag\chunking\languages\css.py` | 253 | 17 | 93% | 37, 93-96, 154-160, 292, 305, 459-464 |
| `src\acolyte\rag\chunking\languages\default.py`| 303 | 16 | 95% | 122, 130, 193, 388, 440, 444, 457, 614, 640, 687-688, 690-691, 708, 712, 718 |
| `src\acolyte\rag\chunking\languages\dockerfile.py`| 130 | 8 | 94% | 83, 129, 228-233, 292 |
| `src\acolyte\rag\chunking\languages\elisp.py` | 163 | 18 | 89% | 39, 137, 197-198, 299, 322-342 |
| `src\acolyte\rag\chunking\languages\go.py` | 369 | 33 | 91% | 74, 127, 156, 233, 266-274, 309, 315-317, 332-338, 376, 399, 503, 516, 519, 555, 565-568, 684 |
| `src\acolyte\rag\chunking\languages\html.py` | 187 | 18 | 90% | 31, 35, 105, 123, 125, 137, 183-184, 257-258, 281, 285, 294, 312-313, 343, 375-376 |
| `src\acolyte\rag\chunking\languages\ini.py` | 353 | 23 | 93% | 212, 377-385, 409, 492-493, 515-517, 535-536, 586-587, 713, 753, 755, 774, 778, 789, 791, 793 |
| `src\acolyte\rag\chunking\languages\java.py` | 317 | 32 | 90% | 34, 165, 266, 438, 474-493, 510-513, 535-536, 582, 606, 608, 610, 612 |
| `src\acolyte\rag\chunking\languages\json.py` | 173 | 4 | 98% | 139, 261, 387, 391 |
| `src\acolyte\rag\chunking\languages\kotlin.py`| 406 | 43 | 89% | 103-105, 190, 195, 200, 205, 210, 223, 228, 233, 238, 243, 247, 281, 289-291, 341-342, 380-400, 404, 457-458, 463, 465, 573, 588, 617, 722, 741 |
| `src\acolyte\rag\chunking\languages\lua.py` | 143 | 15 | 90% | 38, 68-70, 75-80, 84-85, 89-90, 101-102, 118 |
| `src\acolyte\rag\chunking\languages\makefile.py`| 95 | 0 | 100% | |
| `src\acolyte\rag\chunking\languages\markdown.py`| 203 | 6 | 97% | 67, 75, 164, 201, 250, 253 |
| `src\acolyte\rag\chunking\languages\perl.py` | 262 | 32 | 88% | 159, 239, 241, 281, 453, 458-459, 477-480, 484-487, 502-532, 552, 568 |
| `src\acolyte\rag\chunking\languages\php.py` | 346 | 66 | 81% | 45, 120, 181-182, 199-200, 212-218, 265-266, 287, 317-319, 351-352, 366-367, 382-384, 440-452, 461, 472-474, 499-501, 528-529, 565-571, 575-579, 591-597, 604, 608-611, 621, 625 |
| `src\acolyte\rag\chunking\languages\python.py`| 327 | 18 | 94% | 12, 45, 182, 188, 190, 192, 208, 216, 230, 266, 399-400, 546-547, 576-578, 637 |
| `src\acolyte\rag\chunking\languages\r.py` | 267 | 67 | 75% | 32-49, 109-143, 214-215, 236, 268-279, 287-297, 347-367, 487-490 |
| `src\acolyte\rag\chunking\languages\ruby.py` | 542 | 126 | 77% | 139, 160-165, 214-220, 239, 245-247, 252, 288-290, 335-348, 366, 442, 459-465, 511, 549, 631-639, 643-652, 656-666, 668-678, 680-690, 764-773, 798-799, 896-921, 925-943, 961-983 |
| `src\acolyte\rag\chunking\languages\rust.py` | 638 | 70 | 89% | 33, 95, 106, 124, 132-138, 144, 165, 238-240, 244, 247, 268, 271, 333, 351, 360, 380, 389, 391-393, 510-512, 554-555, 557-558, 560-561, 580-581, 583, 585, 606, 633-634, 642, 650, 654, 769-781, 826, 841-842, 917-922, 929-931, 942, 986 |
| `src\acolyte\rag\chunking\languages\sql.py` | 158 | 3 | 98% | 195, 211, 360 |
| `src\acolyte\rag\chunking\languages\swift.py` | 446 | 41 | 91% | 60, 64, 68, 302, 372, 381-385, 398, 504-506, 515, 520, 628, 646, 710, 805-807, 809-811, 813-814, 837, 901, 978, 980, 996, 998, 1000, 1043, 1045, 1057, 1067, 1070, 1073, 1077, 1155, 1197 |
| `src\acolyte\rag\chunking\languages\toml.py` | 95 | 0 | 100% | |
| `src\acolyte\rag\chunking\languages\typescript.py`| 194 | 4 | 98% | 238-239, 306, 404 |
| `src\acolyte\rag\chunking\languages\vim.py` | 313 | 8 | 97% | 201, 237, 411, 481, 495, 504, 587-590 |
| `src\acolyte\rag\chunking\languages\xml.py` | 468 | 52 | 89% | 304, 350-352, 413, 489, 520, 522, 524-527, 678-693, 739-741, 752-754, 891, 988, 1042-1045, 1057-1058, 1074, 1094-1097, 1099-1114, 1125 |
| `src\acolyte\rag\chunking\languages\yaml.py` | 171 | 1 | 99% | 341 |
| `src\acolyte\rag\chunking\mixins.py` | 144 | 3 | 98% | 46, 346, 422 |
| `src\acolyte\rag\collections\__init__.py` | 3 | 0 | 100% | |
| `src\acolyte\rag\collections\collection_names.py`| 13 | 0 | 100% | |
| `src\acolyte\rag\collections\manager.py` | 193 | 15 | 92% | 68-69, 192, 207, 209-210, 230-231, 250, 252-253, 274-275, 302-303 |
| `src\acolyte\rag\compression\__init__.py` | 4 | 0 | 100% | |
| `src\acolyte\rag\compression\chunk_compressor.py`| 190 | 13 | 93% | 176-177, 280-282, 290, 336-339, 420, 433-437 |
| `src\acolyte\rag\compression\contextual.py` | 178 | 17 | 90% | 259-263, 310, 324, 330, 376-378, 440, 450-451, 463, 465, 469-470 |
| `src\acolyte\rag\compression\strategies.py` | 270 | 25 | 91% | 204-208, 279-291, 338, 351, 406-414, 435, 459 |
| `src\acolyte\rag\enrichment\__init__.py` | 2 | 0 | 100% | |
| `src\acolyte\rag\enrichment\processors\__init__.py`| 2 | 0 | 100% | |
| `src\acolyte\rag\enrichment\processors\graph_builder.py`| 106 | 4 | 96% | 196, 222-224 |
| `src\acolyte\rag\enrichment\service.py` | 433 | 46 | 89% | 56, 183-186, 295-297, 367-370, 425, 427, 474, 478-483, 516-517, 521-522, 559-560, 572-574, 636-638, 649, 678-679, 718, 736, 741, 746, 748, 751, 753, 771, 773, 855, 891, 941-943 |
| `src\acolyte\rag\graph\__init__.py` | 4 | 0 | 100% | |
| `src\acolyte\rag\graph\neural_graph.py` | 111 | 3 | 97% | 138, 173, 267 |
| `src\acolyte\rag\graph\pattern_detector.py` | 70 | 3 | 96% | 278-280 |
| `src\acolyte\rag\graph\relations_manager.py` | 77 | 0 | 100% | |
| `src\acolyte\rag\retrieval\__init__.py` | 7 | 0 | 100% | |
| `src\acolyte\rag\retrieval\cache.py` | 82 | 0 | 100% | |
| `src\acolyte\rag\retrieval\filters.py` | 127 | 6 | 95% | 85-91, 240, 307 |
| `src\acolyte\rag\retrieval\fuzzy_matcher.py`| 156 | 4 | 97% | 89, 153, 317-318 |
| `src\acolyte\rag\retrieval\hybrid_search.py`| 257 | 22 | 91% | 189-190, 211-212, 305, 317, 358-360, 408-442, 547 |
| `src\acolyte\rag\retrieval\metrics.py` | 91 | 1 | 99% | 104 |
| `src\acolyte\rag\retrieval\rerank.py` | 87 | 3 | 97% | 75-78 |
| `src\acolyte\semantic\__init__.py` | 8 | 0 | 100% | |
| `src\acolyte\semantic\decision_detector.py` | 161 | 20 | 88% | 110, 112, 117, 137, 218-221, 228-233, 270, 298-306, 314 |
| `src\acolyte\semantic\prompt_builder.py` | 109 | 0 | 100% | |
| `src\acolyte\semantic\query_analyzer.py` | 72 | 1 | 99% | 134 |
| `src\acolyte\semantic\reference_resolver.py`| 64 | 0 | 100% | |
| `src\acolyte\semantic\summarizer.py` | 110 | 3 | 97% | 181, 192, 224 |
| `src\acolyte\semantic\task_detector.py` | 90 | 2 | 98% | 126, 138 |
| `src\acolyte\semantic\utils.py` | 33 | 0 | 100% | |
| `src\acolyte\services\__init__.py` | 6 | 0 | 100% | |
| `src\acolyte\services\chat_service.py` | 282 | 15 | 95% | 262-263, 407-411, 416-417, 438, 440, 442, 444, 449, 457, 590, 609, 750 |
| `src\acolyte\services\conversation_service.py`| 302 | 21 | 93% | 434-436, 488, 513-519, 556, 573-579, 648-650, 791-793 |
| `src\acolyte\services\git_service.py` | 220 | 9 | 96% | 117-118, 125-126, 205, 213, 483, 504-507 |
| `src\acolyte\services\indexing_service.py` | 474 | 34 | 93% | 27-29, 35-37, 46-48, 391, 409, 454, 556, 728, 912, 918-920, 924, 928, 1026-1028, 1144-1146, 1224-1240 |
| `src\acolyte\services\task_service.py` | 149 | 3 | 98% | 266-268 |
| **TOTAL** | **19288** | **1297** | **93%** | **3.511 TESTS PASSED - in 136s**  |
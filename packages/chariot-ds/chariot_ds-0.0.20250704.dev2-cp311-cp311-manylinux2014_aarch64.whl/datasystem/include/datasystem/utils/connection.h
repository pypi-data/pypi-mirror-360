/**
 * Copyright (c) Huawei Technologies Co., Ltd. 2022. All rights reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
#ifndef DATASYSTEM_UTILS_CONNECTION_H
#define DATASYSTEM_UTILS_CONNECTION_H

#include <string>

#include "datasystem/utils/sensitive_value.h"
#include "datasystem/utils/string_view.h"
#include "datasystem/object_cache/object_enum.h"

namespace datasystem {
struct ConnectOptions {
    std::string host;
    int32_t port;
    int32_t connectTimeoutMs = 60 * 1000;  // 60s
    std::string clientPublicKey = "";
    SensitiveValue clientPrivateKey = "";
    std::string serverPublicKey = "";
    std::string accessKey = "";
    SensitiveValue secretKey = "";
    std::string tenantId = "";
    bool enableCrossNodeConnection = false;
};
}  // namespace datasystem

#endif  // DATASYSTEM_UTILS_CONNECTION_H

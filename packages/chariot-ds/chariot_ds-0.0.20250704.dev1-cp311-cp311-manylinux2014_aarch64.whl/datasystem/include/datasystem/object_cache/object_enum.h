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

/**
 * Description: Defines the object enum value.
 */
#ifndef DATASYSTEM_OBJECT_ENUM_H
#define DATASYSTEM_OBJECT_ENUM_H

#include <cstdint>
#include <memory>

#include "datasystem/utils/status.h"

namespace datasystem {

/// \brief WriteMode defines the reliability of object.
enum class WriteMode : int {
    NONE_L2_CACHE = 0,          /**< Object only store in cache. Default mode. */
    WRITE_THROUGH_L2_CACHE = 1, /**< Object store in cache and synchronized to L2. */
    WRITE_BACK_L2_CACHE = 2,    /**< Object store in cache and asynchronized to L2. */
    NONE_L2_CACHE_EVICT = 3,    /**< Object is volatile, if cache resources are lacking, it will be deleted. */
};

/// \brief ConsistencyType class defines the consistency of object.
enum class ConsistencyType : int {
    PRAM = 0,   /**< PRAM (Pipelined RAM) consistency. */
    CAUSAL = 1, /**< Causal consistency. */
};
}  // namespace datasystem
#endif  // DATASYSTEM_OBJECT_ENUM_H

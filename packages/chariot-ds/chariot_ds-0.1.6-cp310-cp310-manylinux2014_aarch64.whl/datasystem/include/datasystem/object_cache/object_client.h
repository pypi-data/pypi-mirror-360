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
 * Description: Data system object cache client management.
 */

#ifndef DATASYSTEM_OBJECT_CACHE_OBJECT_CLIENT_H
#define DATASYSTEM_OBJECT_CACHE_OBJECT_CLIENT_H

#include <functional>
#include <iostream>
#include <memory>
#include <mutex>
#include <unordered_map>
#include <unordered_set>
#include <vector>

#include "datasystem/object_cache/buffer.h"
#include "datasystem/object_cache/object_enum.h"
#include "datasystem/utils/connection.h"
#include "datasystem/utils/optional.h"
#include "datasystem/utils/status.h"

namespace datasystem {
namespace object_cache {
class ObjectClientImpl;
}  // namespace object_cache
}  // namespace datasystem

namespace datasystem {

/// \brief CreateParam defines the parameters for `create` function.
struct CreateParam {
    WriteMode writeMode = WriteMode::NONE_L2_CACHE;          /**< Reliability. */
    ConsistencyType consistencyType = ConsistencyType::PRAM; /**< Consistency. */
};

struct ObjMetaInfo {
    uint64_t objSize{ 0 };               // the size of object data, 0 if object not found.
    std::vector<std::string> locations;  // the workerIds of the locations
};

class __attribute((visibility("default"))) ObjectClient : public std::enable_shared_from_this<ObjectClient> {
public:
    /// \brief Construct ObjectClient.
    ///
    /// \param[in] connectOptions The connection options.
    explicit ObjectClient(const ConnectOptions &connectOptions = {});

    ~ObjectClient();

    /// \brief Shutdown the object client.
    ///
    /// \return K_OK on success; the error code otherwise.
    Status ShutDown();

    /// \brief Init the object client.
    ///
    /// \return K_OK on success; the error code otherwise.
    Status Init();

    /// \brief Increase the global reference count to objects in the data system.
    ///
    /// \param[in] objectKeys The object keys to be increased, `objectKeys` cannot be empty. Key should not be empty
    ///  (zero-length) and should only contain English alphabetics characters(a-zA-Z), digits and special characters
    ///  `~!@#$%^&*.-_` . Key length must be less than 256 characters. The max objectKeys size <= 10000.
    /// \param[out] failedObjectKeys Increase failed object keys.
    ///
    /// \return K_OK if at least one object key is successfully processed, `failedObjectKeys` indicate the failed
    ///  list.
    ///         - K_RPC_UNAVAILABLE: Disconnect from worker.
    ///         - K_INVALID: The parameter is invalid.
    Status GIncreaseRef(const std::vector<std::string> &objectKeys, std::vector<std::string> &failedObjectKeys);

    /// \brief Decrease the global reference count to objects in the data system.
    ///
    /// \param[in] objectKeys The object keys to be increased, objectKeys cannot be empty. Key should not be empty
    ///  (zero-length) and should only contain English alphabetics characters(a-zA-Z), digits and special characters
    ///  `~!@#$%^&*.-_` . Key length must be less than 256 characters. The max objectKeys size <= 10000.
    /// \param[out] failedObjectKeys Decrease failed object keys.
    ///
    /// \return K_OK if at least one object key is successfully processed, `failedObjectKeys` indicate the failed
    ///  list.
    ///         - K_RPC_UNAVAILABLE: Disconnect from worker.
    ///         - K_INVALID: The parameter is invalid.
    Status GDecreaseRef(const std::vector<std::string> &objectKeys, std::vector<std::string> &failedObjectKeys);

    /// \brief Query the global references of specified object key. (Out-of-cloud references not included)
    ///
    /// \param[in] objectKey The key of the object to be created. Object keys must be non-empty (1–255 characters),
    ///  and can only contain English letters (a-zA-Z), digits (0-9), or special characters `~!@#$%^&*.-_`.
    ///
    /// \return The objects' global reference num; -1 in case of failure.
    int QueryGlobalRefNum(const std::string &objectKey);

    /// \brief Invoke worker client to create an object.
    ///
    /// \param[in] objectKey The key of the object to be created. Object keys must be non-empty (1–255 characters),
    ///  and can only contain English letters (a-zA-Z), digits (0-9), or special characters `~!@#$%^&*.-_`.
    /// \param[in] size The object size in bytes.
    /// \param[in] param Create parameter.
    /// \param[out] buffer The buffer for the object.
    ///
    /// \return K_OK on success; the error code otherwise.
    ///         - K_INVALID: the object key or value is empty.
    ///         - K_RUNTIME_ERROR: client fd mmap failed
    Status Create(const std::string &objectKey, uint64_t size, const CreateParam &param,
                  std::shared_ptr<Buffer> &buffer);

    /// \brief Invoke worker client to put an object (publish semantics).
    ///
    /// \param[in] objectKey The key of the object to be created. Object keys must be non-empty (1–255 characters),
    ///  and can only contain English letters (a-zA-Z), digits (0-9), or special characters `~!@#$%^&*.-_`.
    /// \param[in] data The data pointer of the user.
    /// \param[in] size The object size in bytes.
    /// \param[in] param Create parameters.
    /// \param[in] nestedObjectKeys Objects that depend on objectKey.
    ///
    /// \return K_OK on success; the error code otherwise.
    Status Put(const std::string &objectKey, const uint8_t *data, uint64_t size, const CreateParam &param,
               const std::unordered_set<std::string> &nestedObjectKeys = {});

    /// \brief Invoke worker client to get all buffers of all the given object keys.
    ///
    /// \param[in] objectKeys The object keys to be increased, `objectKeys` cannot be empty. Key should not be empty
    ///  (zero-length) and should only contain English alphabetics characters(a-zA-Z), digits and special characters
    ///  `~!@#$%^&*.-_` . Key length must be less than 256 characters. The max objectKeys size <= 10000.
    /// \param[in] subTimeoutMs The maximum amount of time in milliseconds to wait before returning. Set this to
    ///  positive number will block until the corresponding object becomes available. Setting `subTimeoutMs=0` will
    ///  return the object immediately if it’s available, else return `K_NOT_FOUND` indicates that the object is
    ///  unavailable. 0 means no waiting time allowed.
    /// \param[out] buffers The return vector of the object keys.
    ///
    /// \return K_OK if at least one object key is successfully got; the error code otherwise.
    ///         - K_INVALID: `objectKeys` is empty or contains empty (zero-length) key.
    ///         - K_NOT_FOUND: all object keys do not exist.
    ///         - K_RUNTIME_ERROR: Cannot get objects from worker.
    Status Get(const std::vector<std::string> &objectKeys, int32_t subTimeoutMs,
               std::vector<Optional<Buffer>> &buffers);

    /// \brief Add the workerUuid as a suffix to the objectKey.
    ///
    /// \param[in] prefix The objectKey generated by user.
    /// \param[out] objectKey The key with worker UUID.
    ///
    /// \return K_OK on success; the error code otherwise.
    Status GenerateObjectKey(const std::string &prefix, std::string &objectKey);

    /// \brief Worker health check.
    ///
    /// \return K_OK on success; the error code otherwise.
    Status HealthCheck();

private:
    std::shared_ptr<object_cache::ObjectClientImpl> impl_;
};
}  // namespace datasystem
#endif  // DATASYSTEM_OBJECT_CACHE_OBJECT_CLIENT_H

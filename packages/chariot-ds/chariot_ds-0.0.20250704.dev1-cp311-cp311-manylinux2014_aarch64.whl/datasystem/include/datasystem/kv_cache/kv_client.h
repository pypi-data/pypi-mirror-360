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
 * Description: Data system state cache client management.
 */
#ifndef DATASYSTEM_KV_CACHE_KV_CLIENT_H
#define DATASYSTEM_KV_CACHE_KV_CLIENT_H

#include <memory>
#include <unordered_map>
#include <vector>

#include "datasystem/object_cache/buffer.h"
#include "datasystem/object_cache/object_enum.h"
#include "datasystem/kv_cache/read_only_buffer.h"
#include "datasystem/utils/connection.h"
#include "datasystem/utils/optional.h"
#include "datasystem/utils/status.h"
#include "datasystem/utils/string_view.h"

namespace datasystem {
namespace object_cache {
class ObjectClientImpl;
}  // namespace object_cache
}  // namespace datasystem

namespace datasystem {
enum class ExistenceOpt : int {
    NONE = 0,  // Does not check for existence.
    NX = 1,    // Only set the key if it does not already exist.
};
struct SetParam {
    WriteMode writeMode = WriteMode::NONE_L2_CACHE;  // The default value of writeMode is WriteMode::NONE_L2_CACHE.
    // The default value 0 means the key will keep alive until you call Del api to delete the key explicitly.
    uint32_t ttlSecond = 0;
    ExistenceOpt existence = ExistenceOpt::NONE;
};

struct MSetParam {
    WriteMode writeMode = WriteMode::NONE_L2_CACHE;  // The default value of writeMode is WriteMode::NONE_L2_CACHE.
    uint32_t ttlSecond = 0; // The default value means the key will keep alive until you call Del api to delete the key.
    ExistenceOpt existence; // There is not default value, and MSetNx only support NX mode.
};

struct ReadParam {
    std::string key;
    uint64_t offset = 0;
    uint64_t size = 0;
};

class __attribute((visibility("default"))) KVClient {
public:
    /// \brief Construct KVClient.
    ///
    /// \param[in] connectOptions The connection options.
    explicit KVClient(const ConnectOptions &connectOptions = {});

    ~KVClient();

    /// \brief Shutdown the state client.
    ///
    /// \return K_OK on success; the error code otherwise.
    Status ShutDown();

    /// \brief Init KVClient instance.
    ///
    /// \return Status of the call.
    Status Init();

    /// \brief Invoke worker client to set the value of a key.
    ///
    /// \param[in] key The key to be processed, must be non-empty (1–255 characters), and can only contain
    ///  English letters (a-zA-Z), digits (0-9), or special characters `~!@#$%^&*.-_`.
    /// \param[in] val The value for the key.
    /// \param[in] param The get parameters.
    ///
    /// \return K_OK on success; the error code otherwise.
    ///         K_INVALID: the key or value is empty.
    Status Set(const std::string &key, const StringView &val, const SetParam &param = {});

    /// \brief Invoke worker client to set the value of a key.
    ///
    /// \param[in] val The value for the key.
    /// \param[in] param The get parameters.
    ///
    /// \return The key name, return empty string if set error.
    std::string Set(const StringView &val, const SetParam &param = {});

    /// \brief Transactional multi-key set interface, it guarantees all the keys are either successfully created or
    ///  none of them is created. The number of keys should be in the range of 1 to 8.
    ///
    /// \param[in] keys A vector of strings representing the keys to be set. Must not be empty and should
    ///  contain no empty strings.
    /// \param[in] vals The values for the keys.
    /// \param[in] param The set parameters.
    ///
    /// \return K_OK on success; the error code otherwise.
    Status MSetTx(const std::vector<std::string> &keys, const std::vector<StringView> &vals,
                  const MSetParam &param = {});

    /// \brief Multi-key set interface, it can batch set keys and return failed keys. The max keys size < 2000
    ///  and the max value for key to set < 500 * 1024
    ///
    /// \param[in] keys A vector of strings representing the keys to be set. Must not be empty and should
    ///  contain no empty strings.
    /// \param[in] vals The values to set
    /// \param[out] outFailedKeys The failed keys for set
    /// \param[in] param The set parameters.
    ///
    /// \return K_OK if at least one key is successfully processed; the error code otherwise.
    Status MSet(const std::vector<std::string> &keys, const std::vector<StringView> &vals,
                std::vector<std::string> &outFailedKeys, const MSetParam &param = {});

    /// \brief Invoke worker client to get the value of a key.
    ///
    /// \param[in] key The key to be processed, must be non-empty (1–255 characters), and can only contain
    ///  English letters (a-zA-Z), digits (0-9), or special characters `~!@#$%^&*.-_`.
    /// \param[out] val The value for the key.
    /// \param[in] subTimeoutMs The maximum amount of time in milliseconds to wait before returning. Set this to
    ///  positive number will block until the corresponding key becomes available. Setting `subTimeoutMs=0` will
    ///  return the value immediately if it’s available, else return `K_NOT_FOUND` indicates that the key is
    ///  unavailable. 0 means no waiting time allowed.
    ///
    /// \return K_OK on success; the error code otherwise.
    ///         - K_INVALID: the key is empty.
    ///         - K_NOT_FOUND: the key is not found.
    ///         - K_RUNTIME_ERROR: Cannot get value from worker.
    Status Get(const std::string &key, std::string &val, int32_t subTimeoutMs = 0);

    /// \brief Invoke worker client to get the value of a key.
    ///
    /// \param[in] key The key to be processed, must be non-empty (1–255 characters), and can only contain
    ///  English letters (a-zA-Z), digits (0-9), or special characters `~!@#$%^&*.-_`.
    /// \param[in] subTimeoutMs The maximum amount of time in milliseconds to wait before returning. Set this to
    ///  positive number will block until the corresponding key becomes available. Setting `subTimeoutMs=0` will
    ///  return the value immediately if it’s available, else return `K_NOT_FOUND` indicates that the key is
    ///  unavailable. 0 means no waiting time allowed.
    /// \param[out] readOnlyBuffer The value for the key.
    ///
    /// \return K_OK on success; the error code otherwise.
    ///         - K_INVALID: the key is empty.
    ///         - K_NOT_FOUND: the key is not found.
    ///         - K_RUNTIME_ERROR: Cannot get value from worker.
    Status Get(const std::string &key, Optional<ReadOnlyBuffer> &readOnlyBuffer, int32_t subTimeoutMs = 0);

    /// \brief Invoke worker client to get the values of all the given keys.
    ///
    /// \param[in] keys The vector of the keys. Constraint: The number of keys cannot exceed 10,000.
    /// \param[in] subTimeoutMs The maximum amount of time in milliseconds to wait before returning. Setting this to
    ///  a positive number will block until the corresponding keys become available. Setting `subTimeoutMs=0` will
    ///  return the values immediately if they are available; otherwise, it returns `K_NOT_FOUND` to indicate that all
    ///  keys are unavailable. 0 means no waiting time is allowed.
    /// \param[out] vals The vector of the values.
    ///
    /// \return K_OK if at least one key is successfully got; the error code otherwise.
    ///         - K_INVALID: The vector of `keys` is empty or include empty (zero-length) elements.
    ///         - K_NOT_FOUND: all keys are not found.
    ///         - K_RUNTIME_ERROR: Cannot get values from worker.
    /// \verbatim
    ///  Status OK will be returned if some keys are not found,
    ///  and the existing keys will set the vals with the same index of keys.
    /// \endverbatim
    Status Get(const std::vector<std::string> &keys, std::vector<std::string> &vals, int32_t subTimeoutMs = 0);

    /// \brief Invoke worker client to get the values of all the given keys.
    ///
    /// \param[in] keys The vector of the keys. Constraint: The number of keys cannot exceed 10,000.
    /// \param[in] subTimeoutMs The maximum amount of time in milliseconds to wait before returning. Setting this to
    ///  a positive number will block until the corresponding keys become available. Setting `subTimeoutMs=0` will
    ///  return the values immediately if they are available; otherwise, it returns `K_NOT_FOUND` to indicate that all
    ///  keys are unavailable. 0 means no waiting time is allowed.
    /// \param[out] readOnlyBuffers The vector of the values.
    ///
    /// \return K_OK if at least one key is successfully got; the error code otherwise.
    ///         - K_INVALID: The vector of `keys` is empty or include empty (zero-length) elements.
    ///         - K_NOT_FOUND: all keys are not found.
    ///         - K_RUNTIME_ERROR: Cannot get values from worker.
    /// \verbatim
    ///  Status OK will be returned if some keys are not found,
    ///  and the existing keys will set the vals with the same index of keys.
    /// \endverbatim
    Status Get(const std::vector<std::string> &keys, std::vector<Optional<ReadOnlyBuffer>> &readOnlyBuffers,
               int32_t subTimeoutMs = 0);

    /// \brief Some data in a key can be read based on the specified key and parameters.
    ///         In some scenarios, read amplification can be avoided.
    ///
    /// \param[in] readParams The vector of the keys and offset. Constraint: The number of readParam
    ///  cannot exceed 10000.
    /// \param[out] readOnlyBuffers The vector of the values.
    ///
    /// \return K_OK if at least one key is successfully read; the error code otherwise.
    ///         - K_INVALID: The vector of `keys` is empty or include empty (zero-length) elements.
    ///         - K_NOT_FOUND: the key is not found.
    ///         - K_RUNTIME_ERROR: Cannot get values from worker.
    /// \verbatim
    ///  Status OK will be returned if some keys are not found,
    ///  and the existing keys will set the vals with the same index of keys.
    /// \endverbatim
    Status Read(const std::vector<ReadParam> &readParams, std::vector<Optional<ReadOnlyBuffer>> &readOnlyBuffers);

    /// \brief Invoke worker client to delete a key.
    ///
    /// \param[in] key The key to be processed, must be non-empty (1–255 characters), and can only contain
    ///  English letters (a-zA-Z), digits (0-9), or special characters `~!@#$%^&*.-_`.
    ///
    /// \return K_OK on success; the error code otherwise.
    ///         K_INVALID: The key is empty.
    Status Del(const std::string &key);

    /// \brief Invoke worker client to delete all the given keys.
    ///
    /// \param[in] keys The vector of the keys. Constraint: The number of keys cannot exceed 10,000.
    /// \param[out] failedKeys The failed delete keys.
    ///
    /// \return K_OK if at least one key is successfully processed; the error code otherwise.
    ///         - K_INVALID: The vector of `keys` is empty or include empty (zero-length) elements.
    Status Del(const std::vector<std::string> &keys, std::vector<std::string> &failedKeys);

    /// \brief Generate a key with workerId.
    ///
    /// \param[in] prefixKey The user specified key prefix.
    /// \param[out] key The key to be processed, must be non-empty (1–255 characters), and can only contain
    ///  English letters (a-zA-Z), digits (0-9), or special characters `~!@#$%^&*.-_`.
    ///
    /// \return K_OK on any object success; the error code otherwise.
    Status GenerateKey(const std::string &prefixKey, std::string &key);

    /// \brief Worker health check.
    ///
    /// \return K_OK on any object success; the error code otherwise.
    Status HealthCheck();

private:
    std::shared_ptr<object_cache::ObjectClientImpl> impl_;
};
}  // namespace datasystem
#endif  // DATASYSTEM_KV_CACHE_KV_CLIENT_H

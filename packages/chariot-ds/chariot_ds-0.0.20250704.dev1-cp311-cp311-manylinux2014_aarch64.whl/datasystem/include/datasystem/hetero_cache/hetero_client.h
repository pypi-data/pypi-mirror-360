/**
 * Copyright (c) Huawei Technologies Co., Ltd. 2024. All rights reserved.
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
 * Description: Data system Hetero cache client management.
 */

#ifndef DATASYSTEM_HETERO_CACHE_HETERO_CLIENT_H
#define DATASYSTEM_HETERO_CACHE_HETERO_CLIENT_H

#include <future>
#include <vector>

#include "datasystem/hetero_cache/future.h"
#include "datasystem/utils/connection.h"
#include "datasystem/utils/status.h"

namespace datasystem {
namespace object_cache {
class ObjectClientImpl;
}  // namespace object_cache
}  // namespace datasystem

namespace datasystem {

/// \brief Blob defines a memory segment on a device NPU.
struct Blob {
    void *pointer = 0; /**< Blob memory address. */
    uint64_t size = 0; /**< Blob size in bytes. */
};

/// \brief DeviceBlobList defines a group of memory on a device. Information about each memory segment is stored in a
///  Blob.
///
/// \note The blobs under the same DeviceBlobList need to be under the same card.
struct DeviceBlobList {
    std::vector<Blob> blobs; /**< Blob list. */
    int32_t deviceIdx = -1;  /**< Device index. */
};

struct AsyncResult {
    Status status;
    std::vector<std::string> failedList;
};
class __attribute((visibility("default"))) HeteroClient : public std::enable_shared_from_this<HeteroClient> {
public:
    /// \brief Constructor a HeteroClient.
    /// \param[in] connectOptions The connection options.
    explicit HeteroClient(const ConnectOptions &connectOptions = {});

    /// \brief Destructor.
    ~HeteroClient();

    /// \brief Shutdown the HeteroClient and disconnect it from the data system Worker.
    /// \return K_OK on success; the error code otherwise.
    Status ShutDown();

    /// \brief Init HeteroClient object and establishes a connection with the data system Worker.
    /// \return Status of the call.
    Status Init();

    /// \brief Obtain data from the host and write the data to the device.
    ///     MGetH2D and MSetD2H must be used together.
    ///     If multiple memory addresses are combined and written to the host during MSetD2H, the host data
    ///     is automatically split into multiple memory addresses and written to the device in MGetH2D.
    ///     If the key of the host is no longer used, you can call the Delete interface to delete it.
    /// \param[in] keys Keys in the host. Constraint: The number of keys cannot exceed 10,000.
    /// \param[out] devBlobList Address of the HBM pointer on the device. Data read from the host key is written to
    ///     these pointers.
    /// \param[out] failedKeys failed keys to be get
    /// \param[in] subTimeoutMs max waiting time of getting data
    /// \return K_OK if at least one key is successfully processed; the error code otherwise.
    Status MGetH2D(const std::vector<std::string> &keys, const std::vector<DeviceBlobList> &devBlobList,
                   std::vector<std::string> &failedKeys, int32_t subTimeoutMs);

    /// \brief Write the data of the device to the host. If the BLOB of the device contains multiple memory addresses,
    ///     the device automatically combines data and writes the data to the host.
    ///     If the key of the host is no longer used, you can call the Delete interface to delete it.
    /// \param[in] keys Keys in the host. Constraint: The number of keys cannot exceed 10,000.
    /// \param[in] devBlobList Pointers to the HBM memory in a group of devices. Data is obtained from these pointers
    ///     and written to the key of the host. If the DeviceBlobList contains multiple HBM pointers, the data is
    ///     combined and written to the shared memory corresponding to the host key.
    /// \return K_OK if at least one key is successfully processed; the error code otherwise.
    Status MSetD2H(const std::vector<std::string> &keys, const std::vector<DeviceBlobList> &devBlobList);

    /// \brief Delete the key from the host. The Delete interface works with MGetH2D and MSetD2H.
    /// \param[in] keys Keys in the host. Constraint: The number of keys cannot exceed 10,000.
    /// \param[out] failedKeys The failed delete keys.
    /// \return K_OK on any key success; the error code otherwise.
    ///         - K_INVALID: The vector of `keys` is empty or include empty (zero-length) elements.
    Status Delete(const std::vector<std::string> &keys, std::vector<std::string> &failedKeys);

    /// @brief For device object Async set multiple objects, and return before publish rpc called.
    /// \param[in] keys Keys in the host. Constraint: The number of keys cannot exceed 10,000.
    /// \param[in] devBlobList Pointers to the HBM memory in a group of devices. Data is obtained from these pointers
    ///     and written to the key of the host. If the DeviceBlobList contains multiple HBM pointers, the data is
    ///     combined and written to the shared memory corresponding to the host key.
    /// @return future of AsyncResult, describe set status and failed list.
    std::shared_future<AsyncResult> AsyncMSetD2H(const std::vector<std::string> &keys,
                                                 const std::vector<DeviceBlobList> &devBlobList);

    /// @brief For device object, to async get multiple objects
    /// \param[in] keys Keys in the host. Constraint: The number of keys cannot exceed 10,000.
    /// \param[in] devBlobList Address of the HBM pointer on the device. Data read from the host key is written to
    ///     these pointers.
    /// \param[in] subTimeoutMs max waiting time of getting data
    /// \return future of AsyncResult, describe get status and failed list.
    std::shared_future<AsyncResult> AsyncMGetH2D(const std::vector<std::string> &keys,
                                                 const std::vector<DeviceBlobList> &devBlobList, uint64_t subTimeoutMs);

    /// \brief Add the workerUuid as a suffix to the key.
    /// \param[in] prefix The key generated by user.
    /// \param[out] key The key with workerUuid.
    /// \return K_OK if at least one key is successfully processed; the error code otherwise.
    Status GenerateKey(const std::string &prefix, std::string &key);

    /// \brief Publish the memory on the device as a heterogeneous object of the data system.
    ///     Heterogeneous objects can be obtained through DevSubscribe.
    ///     DevPublish and DevSubscribe must be used together. After data is obtained through DevSubscribe,
    ///     the data system automatically deletes the heterogeneous object and does not manage the device memory
    ///     corresponding to the object.
    ///     The device memory addresses in the input parameters of the DevPublish and DevSubscribe interfaces cannot
    ///     belong to the same NPU.
    /// \param[in] keys Key of the heterogeneous object of the device.
    /// \param[in] devBlobList A list of structures describing the device memory.
    /// \param[out] futureVec A list of futures to track the operation.
    /// \return K_OK on when all futures succeed; the error code otherwise.
    Status DevPublish(const std::vector<std::string> &keys, const std::vector<DeviceBlobList> &devBlobList,
                      std::vector<Future> &futureVec);

    /// \brief Subscribes to heterogeneous objects of the data system and writes data to devBlobList.
    ///     Data is directly transmitted through the device-to-device channel.
    ///     DevPublish and DevSubscribe must be used together. After data is obtained through DevSubscribe,
    ///     the data system automatically deletes the heterogeneous object and does not manage the device memory
    ///     corresponding to the object.
    ///     The device memory addresses in the input parameters of the DevPublish and DevSubscribe interfaces cannot
    ///     belong to the same NPU.
    ///     During the execution of DevSubscribe, do not exit the process where DevPublish is executed. Otherwise,
    ///     DevSubscribe fails.
    /// \param[in] keys Specifies the key of the heterogeneous object of the device.
    /// \param[in] devBlobList Describes the memory structure list on the device and is used to receive data.
    /// \param[out] futureVec A list of futures to track the operation.
    /// \return K_OK on when all futures succeed; the error code otherwise.
    Status DevSubscribe(const std::vector<std::string> &keys, const std::vector<DeviceBlobList> &devBlobList,
                        std::vector<Future> &futureVec);

    /// \brief Obtains data from the device and writes the data to devBlobList. Data is transmitted directly through
    ///     the device-to-device channel.
    ///     DevMSet and DevMGet must be used together. Heterogeneous objects are not automatically deleted after
    ///     DevMGet is executed. If an object is no longer used, invoke DevLocalDelete or DevDelete to delete it.
    ///     The device memory addresses in the input parameters of the DevMSet and DevMGet interfaces cannot
    ///     belong to the same NPU.
    ///     During the execution of DevMGet, do not exit the process where DevMSet is executed. Otherwise,
    ///     DevMGet fails.
    /// \param[in] keys Keys corresponding to devBlobList. Constraint: The number of keys cannot exceed 10000.
    /// \param[in] devBlobList List describing the structure of Device memory
    /// \param[out] failedKeys Returns failed keys if retrieval fails
    /// \param[in] subTimeoutMs Provides a timeout time, defaulting to 0
    /// \return K_OK if at least one key is successfully processed; the error code otherwise.
    Status DevMGet(const std::vector<std::string> &keys, const std::vector<DeviceBlobList> &devBlobList,
                   std::vector<std::string> &failedKeys, int32_t subTimeoutMs = 0);

    /// \brief The data system caches data on the device and writes the metadata of the key corresponding to
    ///     devBlobList to the data system so that other clients can access the data system.
    ///     DevMSet and DevMGet must be used together. Heterogeneous objects are not automatically deleted after
    ///     DevMGet is executed. If an object is no longer used, invoke DevLocalDelete or DevDelete to delete it.
    ///     The device memory addresses in the input parameters of the DevMSet and DevMGet interfaces cannot
    ///     belong to the same NPU.
    /// \param[in] keys Keys corresponding to devBlobList. Constraint: The number of keys cannot exceed 10000.
    /// \param[in] devBlobList List describing the structure of Device memory
    /// \param[out] failedKeys Returns failed keys if caching fails
    /// \return K_OK if at least one key is successfully processed; the error code otherwise.
    Status DevMSet(const std::vector<std::string> &keys, const std::vector<DeviceBlobList> &devBlobList,
                   std::vector<std::string> &failedKeys);

    /// \brief Delete the device key. After this command is executed, the data system does not manage the device memory
    ///     corresponding to the key.
    ///     The DevDelete interface is used together with the DevMSet / DevMGet interface.
    /// \param[in] keys The keys of the data expected to be deleted. Constraint: The number of keys cannot exceed 10000.
    /// \param[out] failedKeys The failed delete keys.
    /// \return K_OK on any key success; the error code otherwise.
    ///         - K_INVALID: the vector of keys is empty or include empty key.
    Status DevDelete(const std::vector<std::string> &keys, std::vector<std::string> &failedKeys);

    /// \brief DevLocalDelete interface. After calling this interface, the data replica stored in the data system by
    ///     the current client connection will be deleted.
    ///     The DevLocalDelete interface is used together with the DevMSet / DevMGet interface.
    /// \param[in] keys The keys of the data expected to be deleted. Constraint: The number of keys cannot exceed 10000.
    /// \param[out] failedKeys The failed delete keys.
    /// \return K_OK if at least one key is successfully processed; the error code otherwise.
    Status DevLocalDelete(const std::vector<std::string> &keys, std::vector<std::string> &failedKeys);

    /// \brief Check whether the key exists in the data system.
    /// \param[in] keys The keys to be checked. Constraint: The number of keys cannot exceed 10000.
    /// \param[out] exists The existence of the corresponding key.
    /// \return K_OK if at least one key is successfully processed; the error code otherwise.
    Status Exist(const std::vector<std::string> &keys, std::vector<bool> &exists);

private:
    std::shared_ptr<object_cache::ObjectClientImpl> impl_;
};
}  // namespace datasystem
#endif  // DATASYSTEM_OBJECT_CACHE_OBJECT_CLIENT_H
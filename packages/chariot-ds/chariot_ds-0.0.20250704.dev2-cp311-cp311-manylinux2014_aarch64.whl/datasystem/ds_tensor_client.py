# Copyright (c) Huawei Technologies Co., Ltd. 2025. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Datasystem tensor client python interface.
"""
from __future__ import absolute_import

from typing import List

from datasystem.hetero_client import (
    HeteroClient,
    Blob,
    DeviceBlobList,
    Future
)
from datasystem.util import Validator as validator

try:
    from torch import Tensor
except ModuleNotFoundError as e:
    raise ModuleNotFoundError(
        "DsTensorClient requires either torch or mindspore to be installed. Please install the required package."
    ) from e


class DsTensorClient:
    """
    Data system Tensor Cache Client management for python, which provides named object support for
    efficient transfer of Tensor data between D2D or H2D/D2H.

    Args:
        host(str): The host of the worker address.
        port(int): The port of the worker address.
        device_id (int): The identifier of the device.
        connect_timeout_ms(int): The timeout_ms interval for the connection between the client and worker.
        client_public_key(str): The client's public key, for curve authentication.
        client_private_key(str): The client's private key, for curve authentication.
        server_public_key(str): The worker server's public key, for curve authentication.
        access_key(str): The access key used for AK/SK authorization.
        secret_key(str): The secret key used for AK/SK authorization.
        tenant_id(str): The tenant ID.
        enable_cross_node_connection(bool): Indicates whether the client can connect to the standby node.

    Raises:
        TypeError: Raise a type error if the input parameter is invalid.
        RuntimeError: Raise a runtime error if the client failed to invoke api.
    """

    def __init__(
            self,
            host,
            port,
            device_id,
            connect_timeout_ms=60000,
            client_public_key="",
            client_private_key="",
            server_public_key="",
            access_key="",
            secret_key="",
            tenant_id="",
            enable_cross_node_connection=False,
    ):
        args = [
            ["host", host, str],
            ["port", port, int],
            ["device_id", device_id, int],
            ["connect_timeout_ms", connect_timeout_ms, int],
            ["client_public_key", client_public_key, str],
            ["client_private_key", client_private_key, str],
            ["server_public_key", server_public_key, str],
            ["access_key", access_key, str],
            ["secret_key", secret_key, str],
            ["tenant_id", tenant_id, str],
            ["enable_cross_node_connection", enable_cross_node_connection, bool]
        ]
        validator.check_args_types(args)
        self._hetero_client = HeteroClient(
            host,
            port,
            connect_timeout_ms,
            client_public_key,
            client_private_key,
            server_public_key,
            access_key,
            secret_key,
            tenant_id,
            enable_cross_node_connection,
        )
        self._device_id = device_id

    @staticmethod
    def _is_ms_tensor(tensor: Tensor) -> str:
        """check if the tensor is mindspore type"""
        is_ms = (tensor.device.type == "Ascend")
        return is_ms

    @staticmethod
    def _check_tensor_device_type(tensor: Tensor) -> None:
        """check the tensor type"""
        if tensor.device.type not in ["Ascend", "npu"]:
            raise ValueError(f"{tensor.device.type} tensor, not a npu/Ascend tensor")

    def init(self) -> None:
        """
        Init a client to connect to a worker.

        Raises:
            RuntimeError: Raise a runtime error if the client fails to connect to the worker.
        """
        self._hetero_client.init()

    def mset_d2h(self, keys: List[str], tensors: List[Tensor]) -> list:
        """
        Write the tensors of the device to the host. If the data of the device contains multiple memory addresses,
        the device automatically combines data and writes the data to the host.
        If the key of the host is no longer used, you can call the delete interface to delete it.

        Args:
            keys (List[str]): List of keys associated with the tensors.
                              Constraint: The number of keys cannot exceed 10,000.
            tensors (List[Tensor]): List of tensors to send.

        Returns:
            failed_keys(list): The keys that failed to be set.

        Raises:
            RuntimeError: Raise a runtime error if failing to mset_d2h the values of all keys.
            TypeError: Raise a type error if the input parameter is invalid.
        """
        args = [
            ["keys", keys, list],
            ["tensors", tensors, list]
        ]
        validator.check_args_types(args)
        dev_blob_lists = [self._tensor_2_bloblist(tensor) for tensor in tensors]
        return self._hetero_client.mset_d2h(keys, dev_blob_lists)

    def mget_h2d(self, keys: List[str], tensors: List[Tensor], sub_timeout_ms: int = 0) -> list:
        """
        Obtain tensors from the host and write the tensors to the device.
        mget_h2d and mset_d2h must be used together.
        If multiple memory addresses are combined and written to the host during mset_d2h, the host data is
        automatically split into multiple memory addresses and written to the device in mget_h2d.
        If the key of the host is no longer used, you can call the delete interface to delete it.

        Args:
            keys (List[str]): List of keys associated with the tensors.
                              Constraint: The number of keys cannot exceed 10,000.
            tensors (List[Tensor]): List of tensors to store the retrieved data.
            sub_timeout_ms (int, optional): Timeout for the subscription in milliseconds.
                Defaults to 0.

        Returns:
            failed_keys(list): The keys that failed to get.

        Raises:
            RuntimeError: Raise a runtime error if failing to mget_h2d the values of all keys.
            TypeError: Raise a type error if the input parameter is invalid.
        """
        args = [
            ["keys", keys, list],
            ["tensors", tensors, list],
            ["sub_timeout_ms", sub_timeout_ms, int]
        ]
        validator.check_args_types(args)
        dev_blob_lists = [self._tensor_2_bloblist(tensor) for tensor in tensors]
        return self._hetero_client.mget_h2d(keys, dev_blob_lists, sub_timeout_ms)

    def async_mset_d2h(self, keys: List[str], tensors: List[Tensor]) -> Future:
        """
        Write the tensors of the device to the host asynchronously. If the data of the device contains multiple memory
        addresses, the device automatically combines data and writes the data to the host.
        If the key of the host is no longer used, you can call the delete interface to delete it.

        Args:
            keys (List[str]): List of keys associated with the tensors.
                              Constraint: The number of keys cannot exceed 10,000.
            tensors (List[Tensor]): List of tensors to send.

        Returns:
            Future: A Future object representing the asynchronous operations.

        Raises:
            RuntimeError: Raise a runtime error if failing to mset_d2h the values of all keys.
            TypeError: Raise a type error if the input parameter is invalid.
        """
        args = [
            ["keys", keys, list],
            ["tensors", tensors, list]
        ]
        validator.check_args_types(args)
        dev_blob_list = [self._tensor_2_bloblist(tensor) for tensor in tensors]
        return self._hetero_client.async_mset_d2h(keys, dev_blob_list)

    def async_mget_h2d(self, keys: List[str], tensors: List[Tensor], sub_timeout_ms: int = 0) -> Future:
        """
        Obtain tensors from the host and write the tensors to the device asynchronously.
        If multiple memory addresses are combined and written to the host during async_mset_d2h, the host data is
        automatically split into multiple memory addresses and written to the device in async_mget_h2d.
        If the key of the host is no longer used, you can call the delete interface to delete it.

        Args:
            keys (List[str]): List of keys associated with the tensors.
                              Constraint: The number of keys cannot exceed 10,000.
            tensors (List[Tensor]): List of tensors to store the retrieved data.

        Returns:
            Future: A Future object representing the asynchronous operations.

        Raises:
            RuntimeError: Raise a runtime error if failing to async_mset_d2h the values of all keys.
            TypeError: Raise a type error if the input parameter is invalid.
        """
        args = [
            ["keys", keys, list],
            ["tensors", tensors, list],
            ["sub_timeout_ms", sub_timeout_ms, int]
        ]
        validator.check_args_types(args)
        dev_blob_list = [self._tensor_2_bloblist(tensor) for tensor in tensors]
        return self._hetero_client.async_mget_h2d(keys, dev_blob_list, sub_timeout_ms)

    def delete(self, keys: list = None) -> list:
        """
        Delete the tensor datas of keys from worker.
        The delete interface works with mget_h2d and mset_d2h.

        Args:
            keys (List[str], optional): List of keys to delete. Constraint: The number of keys cannot exceed 10,000.

        Returns:
            failed_keys(list): The keys that failed to be deleted.

        Raises:
            RuntimeError: Raise a runtime error if failing to delete the values of all keys.
            TypeError: Raise a type error if the input parameter is invalid.
        """
        args = [
            ["keys", keys, list]
        ]
        validator.check_args_types(args)
        return self._hetero_client.delete(keys)

    def dev_mset(self, keys: List[str], tensors: List[Tensor]) -> list:
        """
        The data system caches data on the device and writes the metadata of the key corresponding to
        tensors to the data system so that other clients can access the data system.
        dev_mset and dev_mget must be used together. Heterogeneous objects are not automatically deleted after
        dev_mget is executed. If an object is no longer used, invoke dev_local_delete or dev_delete to delete it.
        The device memory addresses in the input parameters of the dev_mset and dev_mget interfaces cannot
        belong to the same NPU.

        Args:
            keys(list): A list of keys corresponding to the data_blob_list. Constraint: The number of keys
                        cannot exceed 10,000.
            tensors (List[Tensor]): List of tensors to store the retrieved data.

        Returns:
            failed_keys(list): The failed dev_mset keys.

        Raises:
            RuntimeError: Raise a runtime error if failing to set the value of all keys.
            TypeError: Raise a type error if the input parameter is invalid.
        """
        args = [
            ["keys", keys, list],
            ["tensors", tensors, list]
        ]
        validator.check_args_types(args)
        dev_blob_lists = [self._tensor_2_bloblist(tensor) for tensor in tensors]
        return self._hetero_client.dev_mset(keys, dev_blob_lists)

    def dev_mget(self, keys: List[str], tensors: List[Tensor], sub_timeout_ms: int = 0) -> list:
        """
        Obtains data from the device and writes the data to tensors. Data is transmitted directly through
        the device-to-device channel.
        dev_mset and dev_mget must be used together. Heterogeneous objects are not automatically deleted after
        dev_mget is executed. If an object is no longer used, invoke dev_local_delete or dev_delete to delete it.
        The device memory addresses in the input parameters of the dev_mset and dev_mget interfaces cannot
        belong to the same NPU.
        During the execution of dev_mget, do not exit the process where dev_mset is executed. Otherwise, dev_mget fails.

        Args:
            keys(list): A list of keys corresponding to the data_blob_list. Constraint: The number of keys
                        cannot exceed 10,000.
            tensors (List[Tensor]): List of tensors to store the retrieved data.
            sub_timeout_ms(int): The sub_timeout_ms of the get operation.

        Returns:
            failed_keys(list): The failed dev_mget keys.

        Raises:
            RuntimeError: Raise a runtime error if failing to get the value of all keys.
            TypeError: Raise a type error if the input parameter is invalid.
        """
        args = [
            ["keys", keys, list],
            ["tensors", tensors, list],
            ["sub_timeout_ms", sub_timeout_ms, int]
        ]
        validator.check_args_types(args)
        dev_blob_lists = [self._tensor_2_bloblist(tensor) for tensor in tensors]
        return self._hetero_client.dev_mget(keys, dev_blob_lists, sub_timeout_ms)

    def dev_delete(self, keys: list = None) -> list:
        """
        Delete the device info from the host.
        The dev_delete interface is used together with the dev_mset / dev_mget interface.

        Args:
            keys(list): The data list of string type. Constraint: The number of keys cannot exceed 10,000.

        Returns:
            failed_keys(list): The failed delete keys.

        Raises:
            RuntimeError: Raise a runtime error if fails to delete the value of all keys.
            TypeError: Raise a type error if the input parameter is invalid.
        """
        args = [
            ["keys", keys, list]
        ]
        validator.check_args_types(args)
        return self._hetero_client.dev_delete(keys)

    def dev_local_delete(self, keys) -> list:
        """
        dev_local_delete interface. After calling this interface, the data replica stored in the data system by the
        current client connection will be deleted.
        The dev_local_delete interface is used together with the dev_mset / dev_mget interface.

        Args:
            keys(list): A list of keys corresponding to the data_blob_list. Constraint: The number of keys
                        cannot exceed 10,000.

        Returns:
            failed_keys(list): The keys that failed to be deleted.

        Raises:
            RuntimeError: Raise a runtime error if fails to get the value of all keys.
            TypeError: Raise a type error if the input parameter is invalid.
        """
        args = [
            ["keys", keys, list]
        ]
        validator.check_args_types(args)
        return self._hetero_client.dev_local_delete(keys)

    def dev_send(self, keys: List[str], tensors: List[Tensor]) -> List[Future]:
        """
        Send the tensors cache on the device as a heterogeneous object of the data system.
        Heterogeneous objects can be obtained through dev_recv.
        dev_send and dev_recv must be used together.
        The device memory addresses in the input parameters of the dev_send and dev_recv interfaces cannot
        belong to the same NPU.
        After data is obtained through dev_recv, the data system automatically deletes the heterogeneous object
        and does not manage the device memory corresponding to the object.

        Args:
            keys (List[str]): A list of keys corresponding to the tensor list.
            tensors (List[Tensor]): List of tensors corresponding to the keys.

        Returns:
            List[Future]: A list of Future objects representing the asynchronous operations.

        Raises:
            RuntimeError: Raise a runtime error if failing to dev_send the values of all keys.
            TypeError: Raise a type error if the input parameter is invalid.
        """
        args = [
            ["keys", keys, list],
            ["tensors", tensors, list]
        ]
        validator.check_args_types(args)
        dev_blob_list = [self._tensor_2_bloblist(tensor) for tensor in tensors]
        return self._hetero_client.dev_publish(keys, dev_blob_list)

    def dev_recv(self, keys: List[str], tensors: List[Tensor]) -> List[Future]:
        """
        Receive heterogeneous objects of the data system and writes data to tensors.
        Tensor data is directly transmitted through the device-to-device channel.
        dev_send and dev_recv must be used together.
        The device memory addresses in the input parameters of the dev_send and dev_recv interfaces cannot
        belong to the same NPU.
        After data is obtained through dev_recv, the data system automatically deletes the heterogeneous object
        and does not manage the device memory corresponding to the object.
        During the execution of dev_recv, do not exit the process where dev_send is executed. Otherwise,
        dev_recv fails.

        Args:
            keys (List[str]): A list of keys corresponding to the tensor list.
            tensors (List[Tensor]): List of tensors to store the retrieved data.

        Returns:
            List[Future]: A list of Future objects representing the asynchronous operations.

        Raises:
            RuntimeError: Raise a runtime error if failing to dev_recv the values of all keys.
            TypeError: Raise a type error if the input parameter is invalid.
        """
        args = [
            ["keys", keys, list],
            ["tensors", tensors, list]
        ]
        validator.check_args_types(args)
        dev_blob_list = [self._tensor_2_bloblist(tensor) for tensor in tensors]
        return self._hetero_client.dev_subscribe(keys, dev_blob_list)

    def _get_start_data_ptr(self, tensor: Tensor) -> int:
        if self._is_ms_tensor(tensor):
            element_size = tensor.element_size()
        else:
            element_size = tensor.dtype.itemsize
        return tensor.data_ptr() + (tensor.storage_offset() * element_size)

    def _tensor_2_bloblist(self, tensor: Tensor) -> DeviceBlobList:
        """
        Convert a PyTorch tensor into a DeviceBlobList.

        Args:
            tensor (Tensor): The PyTorch tensor to convert.

        Returns:
            DeviceBlobList: The converted blob list.

        Raises:
            TypeError: If the input is not a PyTorch tensor.
        """
        self._check_tensor_device_type(tensor)
        blob = Blob(self._get_start_data_ptr(tensor), tensor.nbytes)
        return DeviceBlobList(self._device_id, [blob])

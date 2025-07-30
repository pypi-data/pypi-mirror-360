#
# Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
# Holds all the constants used in the module


NVCF_URL_MAPPING: dict[str, str] = {
    "prod": "https://api.nvcf.nvidia.com",
    "stg": "https://stg.api.nvcf.nvidia.com",
    "canary": "https://api.nvcf.nvidia.com",
}

NVCF_GRPC_URL_MAPPING: dict[str, str] = {
    "prod": "grpc.nvcf.nvidia.com:443",
    "stg": "stg.grpc.nvcf.nvidia.com:443",
    "canary": "stg.grpc.nvcf.nvidia.com:443",
}

"""
   Copyright 2019 Yann Dumont

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

__version__ = '1.0.0'
__title__ = 'SNORKELS'
__description__ = 'A lightweight in memory key-value store with on the fly compression.'
__url__ = 'https://github.com/y-du/snorkels'
__author__ = 'Yann Dumont'
__license__ = 'Apache License 2.0'
__copyright__ = 'Copyright (c) 2019 Yann Dumont'


from .kvs import *
import snorkels.ps_adapter

__all__ = (
    kvs.__all__
)
# @Author: Dr. Jeffrey Chijioke-Uche
# @Date: 2025-06-07
# @Description: Describes the QPU Processor Types for Qiskit Connector
# @License: Apache License 2.0  
# @Copyright (c) 2024-2025 Dr. Jeffrey Chijioke-Uche, All Rights Reserved.
# @Copyright by: U.S Copyright Office
# @Date: 2024-03-01
# @Last Modified by: Dr. Jeffrey Chijioke-Uche    
# @Last Modified time: 2025-06-09
# @Description: This module provides a connector to IBM Quantum devices using Qiskit Runtime Service.
# @License: Apache License 2.0 and creative commons license 4.0
# @Purpose: Software designed for Pypi package for Quantum Plan Backend Connection IBM Backend QPUs Compute Resources Information
#
# Any derivative works of this code must retain this copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals. All rights reserved by Dr. Jeffrey Chijioke-Uche.
#_________________________________________________________________________________
# This file is part of the Qiskit Connector Software.
from pathlib import Path
import os

eagle = f"""                                                                         
                 ░▒███▒░▒███▒                                                       
                 ░▒███▒░▒███▒                                              
                 ▒██▒░░░▒█▓██                                              
                ▒█▓▒▒  ░▒██▒█▓░                                            
                ██▒█▒░░░░░▓█░▓█▓▒▓█████▓▒░                                 
               ▒█░█▒      ░▓▓▒▓█▒▒▒░ ░▒▒▒█▓░                               
              ░██▓█▒░   ░▒▒██░█▓▒▓█████▓▒░▓█▓░                             
              ░████▒░   ▓█▓▒▓██▓▒░     ░▒▒▒░▓█▒░                           
              ░▒██▓     █▓█▓█▓░        ░▒▓▒▒▒░██▒░                         
              ░▒██░     █████░         ▒▓▒▒ ▒░▒▒▒██▒                  
                        ▒█░█▒        ░▓▒▒▒▒▒░▒░▒▒▒██▒                      
                        ░▓█▒█▒░     ░▒▓░▒░▒░▒▒░▒ ▒▒▒█▓░                    
                         ░██░██▒  ░▒▓▒▒▒▒░▒░▒░▒▒▒▓░▒░▒█▓░                  
                          ░▓█▒▒██▒░▓▒▒░▒░▒▒░▒░▒░▒░▒▒░▒░▓█▓░                
                            ▒██▒▒█▓░▓▒░▒░▒░▒░▒▒░▒░▒░▒▒░▒░▓█▓░              
                             ░▒██░▒█▒▓█▒▒▒░▒ ▒░▒▒░▒░▒░▒▒▒▒░██▒░            
                               ░▒██░▓█░▓█░▒▒▒▒░▒ ▒▒▒▒░▒░▒▒▒▒░██▒           
                                 ░▒█▓ ▓█ █▓░▓█▒▒▓█▒░░▓▓▒░▒▒▒▒░▓▓░          
                                   ░▓█▓███░█▓▒▓▒▒▒▒▒▒▒▒▒▒▓▒░▒██▒           
                                    ░▒█░▒▒█▓▓██▒░▒█▓▒░▓█▒▒▒▒▓▒░            
                                 ░▓███▒███▒▒█▓▒█▒▒▒░▒░▒▒▒▒▓█░              
                                 ░▓▒▒▒██▒▒██▒▓▒▒██▒▒▒▒▒ ▒█▒█░              
                                 ░▓███▒   ░▒██▒  ▒██░▒▒▒▒▓▓█░              
                                                  ░▒█▓ ▒▒▓▒█░              
                                                    ░▓█▓░▒▓█░              
                                                      ░▓███▒░              
                                                        ░░░                                                                                      
                                  Eagle Quantum Processor                                                      
"""


heron = f"""
                       ░▒████████████▓▒░                                   
                       ░▒▒   ░▒█▓▒░▒░▒▒███▒░                               
                       ░▒████▓▓▒█████▓▒▒░▒▓███▓▒░░                         
                            ░█▒▓█▒░  ░▒██▓▒▒░▒▒▓████▒▒░                    
                            ▒█▒█░  ░▒▓██▓▒▒▒▒▒░▒▓▓▓██▓▒░                   
                            ▓█▓█   ░█▓▒░░░░░░░▒▓████▒▒▒░                   
                            ▓█▒█░  ▒█▒▒▒▒▓▓▓▓▓▓▓▓▓▓▓▓▓▒░                   
                            ▒█░█▒░ ░▓█▒▒▓██▒░                              
                            ░▓█░██▒░░▓██▒░▒█▓▒                             
                             ░▓█▒▒▓░   ░▓██▒▒█▓░                           
                              ░▒██▒░░░░  ░▒█▓░█▓░                          
                              ░░▓▓▓██████▒░░▓█░█▓░                         
                             ▒▓█▒░ ░░░░░░▒█▓░▒█░█░                         
                           ▒██▒░▓████████▓░▓█▒█▒█▒                         
                         ░▓█▓░██▒░      ░▓█▓▓██▒█▒                         
                       ░▒█▓ ▓█░▓▓▒░       ▒█▒██░█░                         
                     ░▒██░▓█░▓▓░▒░▒▓▒░     ▓█▓▒██░                         
                   ░▒██▒▒█▒▒▓░▒▓ ▓▓▒▓░░░  ░██░██░                          
                  ▒▓█▒▒█▓▒▓▒▒▓▒▓█░▒▓░▓▓▒░░▓█▒██▒                           
                ░▓█▒░█▓▒█▒▒▓▒▒█▒▒█▒▓█▒▒▒▒██░██▒                            
              ░▓█▓░▓▓░▓▒░▓▒▒█▒▒█▒▒█▒▒█▒▒██░██░                             
             ▒██░▓▓▒██░▓▓░█▓░█▓▒█▒▒█▓░▓▒▒█▒█▒                              
            ░▒▓▒▒▒██░██░█▓ ██░█▓░██▒▒█░▓▓█░█▒                              
            ░▒▓▒▓▓░██▒▓█░▓█ █▓ ▓█▓░ ▒█▒█░█░█▒                              
             ░▓█▒▓█▒██▓▒▓░▓▓░▓█▓░   ▓█▒█░█░█▒                              
             ░▓▓▒▒▒▒▒░▓▒░▒░▓██▒     ▓█▒█░█░█▒                              
             ░▓█▓▒▒▓███▒▒▓█▓▒       ▒█▒█░█░█▒                              
               ░▒▒▒▒▒░▒▒▒▒░░        ▓█▒█░█░█▒                              
                                    ▓█▒█░█░█▒                              
                                    ▒█▒█░█░█▒                              
                                    ▓█▒█░█░█▒                              
                                    ▒█▒█░█░█▒                              
                                    ▒▓▓▓░█▓█▒                              
                                    ░▒▒▒░▒▓▒░                              
                      Heron Quantum Processor            
"""

flamingo = f"""
                                        ░░░▒▒▒▒▒▒▒░░░                                                 
                                     ░▒▓▓▓▒░░░▒▓▓▓▓▓▒▒░░                                            
                                    ░▒▓▒░▒▒▒▒▒▒▒░░░▒▒▓▓▓░░                                          
                                   ░▒▓▒▒▓▓▒░░░▒▒▓▒░░░░▒▓▓▒░                                         
                                   ░▒█░█▒░ ░▒▓▓▓▓▒░░░▒▒░▓▓░                                         
                                   ░▒█░█▒░ ░▒▒░░░▒▓▓▓▓▓▓░▓▒                                         
                                   ░▒▓▒▓▓▒░░▒▓▓▓▓▓▒░░▒▓██▓▓                                         
                                    ░▒▓▒▒▓▓░░▒░░░     ░░▒▒░                                         
                                     ░▒▓▓░▒▓▓▓░░░       ░░░                                         
                             ░░░▒▒▓▓▓▓▒░▒▓▓░░▓▓▓▒░░                                                 
                          ░░▒▓▓▓▓▓▒▒▒▒▓▓▓▓░▒▓▒░▒▓▓▒░░                                               
                        ░░▒▓█▓░░▒▒▓▓▓▓▒▒░░▒▓▒▒▓▓▒▒▓▓░░                                              
                      ░░▒▓▓▒░▓█▓▓▓▒▒▒▒▓▓▓█▓▒▒▒░▒▓▓░▓▓▒░                                             
                    ░░▒▓▓▒░▓█▓▒░        ░░▒▓▒░░░░▒▓░▓▓░                                             
                   ░▒▓▓▒░▓▓▒░░                   ░▓▓░▓▒░                                            
                 ░░▓▓▒░▓▓░▓▓▒░░░░                 ▒▓░▓▒░                                            
                ░▒▓▓░▓▓░▓▓░▒▒▒▓▓▒░               ░▒▓░▓▒░                                            
               ░▒▓▒▒▓░▒▓░▒▓▒▒▓▒▒▒░              ░▒▓▒▒▓░░                                            
               ░▒▓░▓▒▓▒▒▓▒▒▓▒░▓▓▒░░░░░░░░░░░░░░▒▓▓▒▒▓▒░                                             
               ░▒█▒▓▒░▓▒░▓▓░▓█▓░ ░▓███████████▓▓░░▓▓▒░                                              
               ░▒█▓▒█▒░▓▓░▓█▓░░░▒▓██▓▒░░░░░░░░░▒▓▓▓░░                                               
               ░▒▓░▓▒▓▓░▒█▓▒░░▒▓█▒▒▒▓█▓███████▓▓▒░                                                  
               ░▒▓░▓▓░▒▓▓▒░░▒▓█▒░▓▓▒▒▓░                                                             
               ░░▓▓▒▒▓▓▒░░▒▓█▓░▓█▒▒▒▒▓░                                                             
                ░▒▓█▓▒░░░▓██▒░▒░▒▓█▓▓█▓▓▓▓▓▓▓▓▒▒░                                                   
                 ░░░░░░░▒▓▒░▒░▒▒▒▒▓▓▒▓▒▒▒▒▒▒▒▒▓█▓▒░                                                 
                      ░░▒▓▓█▓▓▓▓▓▓█▓▓█▓▓▓▓▓▓▓▓▒▒▒▒░                                                 
                      ░░▒▒▒▒▒▒▒▒▒▒▓▓▓▓▒▒▒▒▒▒▒▒▓▓▓▒░                                                 
                                 ░▓▓▒▓░       ░░░░                                                  
                                 ░▓▓▒▓░                                                             
                                 ░▓▓▒▓░                                                             
                                 ░▓▓▒▓░                                                             
                                 ░▓▓▒▓░                                                             
                                 ░▓▓▒▓▓▓▒░                                                          
                                 ░▒▓▓▒░▒▒░                                                          
                                 ░░▓▓▓▓▓▒░                                                          
                                ░░░░░░░░                                                            
               Flamingo Quantum Processor
"""

condor = f"""
                        ░░███████▒░░                                             
                       ░████▒░▒▓███▒                                             
                     ░███▓██████████░                                            
                    ░▓████▒█▒ ░▒████░                                            
                    ░██▒████▒  ░████░                                            
                    ░███▓███▒░███████▓░                                          
                     ▒█████░███████░███░                                         
                      ▒▓▒░▓████████████░                                         
                        ▒███▓███░ ░████▓░░                                       
                       ███░███░   ░██████████░░                                  
                      ▒█████▒     ░▓████▓░▓▓█████░░                              
                      ██▓██░   ░▒▓██▓▓▒▓██████░████▒                             
                      ████░ ░▓████▒▒▒▒▒▒▒▓▒▒█████▓██▓░                           
                      ██▒██▒▓██▓████████▓▓▒  ░░███▓██▒                           
                      ▒███████████▒▒▒▒▒▒▒▒░     ░█████▓                          
                       ▒███▓█▒██░                ░█████▒                         
                        ░▓████▓██░███▓░███▒▒███▒░██░████▒                        
                            ▒██▒█████████████▓████████▒██▒                       
                            ░▓██▒██▓█░██▒█▒████▓████▓██▓██▒                      
                              ░██▓███▓█▒█▒██▓█░█▓▓█░██▒████▒                     
                               ▒███▓███░▒▓█▒██▓█▒█▓██░██████░                    
                               ▒█▒███▓▒▒░████░████░█▒██▓█████▒░                  
                               ▒█▒██████████▒███████▓█░████▓███▒                 
                               ▒███████▓██████▓▒███▓██░▓░█▒██▒███▒░              
                               ░██████▒░ ░░▒█████████▓▒▓█████▓▓████░             
                                ░░░░░░░          ░▓██████████▓█████░             
                                                     ░▒████████████░                
                                Condor Quantum Processor                                                                                                                                                                                                                               
"""
###########################################################################

# Processors:
from pathlib import Path
from os import mkdir
import requests

#___________________________________________________________
# Define the directory and filename separately
#____________________________________________________________
local_media_dir = Path("media")
remote_media_dir = "https://github.com/QComputingSoftware/pypi-qiskit-connector/blob/main/media"

eagle_file_name = "eagle-2021-removebg.png"
heron_file_name = "heron-2023-removebg.png"
flamingo_file_name = "flamingo-2025-removebg.png"
condor_file_name = "condor-2023-removebg.png"
egret_file_name = "egret-2023-removebg.png"
falcon_file_name = "falcon-2019-removebg.png"
hummingbird_file_name = "hummingbird-2019-removebg.png"
canary_file_name = "canary-2017-removebg.png"

j_eagle_processor_file_name = "eagle-2021-effects.png"
j_heron_processor_file_name = "heron-2023-effects.png"
j_flamingo_processor_file_name = "flamingo-2025-effects.png"
j_condor_processor_file_name = "condor-2023-effects.png"
j_egret_processor_file_name = "egret-2023-effects.png"
j_falcon_processor_file_name = "falcon-2019-effects.png"
j_hummingbird_processor_file_name = "hummingbird-2019-effects.png"
j_canary_processor_file_name = "canary-2017-effects.png"

processor_family_array = [
    # The processor images
    eagle_file_name,
    heron_file_name,
    flamingo_file_name,
    condor_file_name,
    egret_file_name,
    falcon_file_name,
    hummingbird_file_name,
    canary_file_name,
    # The effects images
    j_eagle_processor_file_name,
    j_heron_processor_file_name,
    j_flamingo_processor_file_name,
    j_condor_processor_file_name,
    j_egret_processor_file_name,
    j_falcon_processor_file_name,
    j_hummingbird_processor_file_name,
    j_canary_processor_file_name
]


#_____________________________________________________________________________________________
# Function to check if a file is readable
#_____________________________________________________________________________________________
def is_file_readable(file_path):
    """

        Checks if a file exists and is readable.

    Args:
        file_path (str or Path): The path to the file.

    Returns:
        bool: True if the file exists and is readable, False otherwise.
    """
    # Create a Path object
    p = Path(file_path)
    if not p.is_file():
        path_doesnot_exists = "0000"
        return False
    if os.access(p, os.R_OK):
        path_exists_and_readable = "1111"
        return True
    else:
        path_exists_but_not_readable = "0001"
        return False

#_____________________________________________________________________________________________
# Check if the media directory exists, if not, create it
#_____________________________________________________________________________________________
if not local_media_dir.exists():
    mkdir(local_media_dir)
def fetch_direct_qpu_processor_media():
  try:
    for processor in processor_family_array:
      direct_image_url = f"{remote_media_dir}/{processor}"
      print(f"Fetching image from: {direct_image_url}")
      if direct_image_url.endswith("eagle-2021-removebg.png"):
          eagle_processor = f"{direct_image_url}/eagle-2021-effects.png"
      elif direct_image_url.endswith("heron-2023-removebg.png"):
          heron_processor = f"{direct_image_url}/heron-2023-effects.png"
      elif direct_image_url.endswith("flamingo-2025-removebg.png"):
          flamingo_processor = f"{direct_image_url}/flamingo-2025-effects.png"
      elif direct_image_url.endswith("condor-2023-removebg.png"):
          condor_processor = f"{direct_image_url}/condor-2023-effects.png"
      elif direct_image_url.endswith("egret-2023-removebg.png"):
          egret_processor = f"{direct_image_url}/egret-2023-effects.png"
      elif direct_image_url.endswith("falcon-2019-removebg.png"):
          falcon_processor = f"{direct_image_url}/falcon-2019-effects.png"
      elif direct_image_url.endswith("hummingbird-2019-removebg.png"):
          hummingbird_processor = f"{direct_image_url}/hummingbird-2019-effects.png"
      elif direct_image_url.endswith("canary-2017-removebg.png"):
          canary_processor = f"{direct_image_url}/canary-2017-effects.png"
  except requests.exceptions.RequestException as e:
      print(f"QPU Processor: EIF-005")

  try:
     if direct_image_url.endswith("eagle-2021-effects.png"):
        j_eagle_processor = f"{direct_image_url}/eagle-2021-effects.png"
     elif direct_image_url.endswith("heron-2023-effects.png"):
        j_heron_processor = f"{direct_image_url}/heron-2023-effects.png"
     elif direct_image_url.endswith("flamingo-2025-effects.png"):
        j_flamingo_processor = f"{direct_image_url}/flamingo-2025-effects.png"
     elif direct_image_url.endswith("condor-2023-effects.png"):
        j_condor_processor = f"{direct_image_url}/condor-2023-effects.png"
     elif direct_image_url.endswith("egret-2023-effects.png"):
        j_egret_processor = f"{direct_image_url}/egret-2023-effects.png"
     elif direct_image_url.endswith("falcon-2019-effects.png"):
        j_falcon_processor = f"{direct_image_url}/falcon-2019-effects.png"
     elif direct_image_url.endswith("hummingbird-2019-effects.png"):
        j_hummingbird_processor = f"{direct_image_url}/hummingbird-2019-effects.png"
     elif direct_image_url.endswith("canary-2017-effects.png"):
        j_canary_processor = f"{direct_image_url}/canary-2017-effects.png"
  except requests.exceptions.RequestException as e:
      print(f"QPU Processor: EIF-006")

#________________________________________________________
# Function to check the status of remote media processor
#________________________________________________________
status_code = 0  # Initialize status_code variable
def remote_media_processor_status():
  for processor in processor_family_array:
      remote_processor_status = f"{remote_media_dir}/{processor}"
  try:
      response = requests.get(remote_processor_status)
      status_code = response.status_code
      if status_code == 200:
          fetch_direct_qpu_processor_media()
  except requests.exceptions.RequestException as e:
      print(f"Msg: REMS-0067")
remote_media_processor_status()


if __name__ == '__main__':
    local_processor_file_status = local_media_dir / eagle_file_name
    is_file_readable(f"{local_processor_file_status}")
    is_file_readable(f"{local_processor_file_status}")

# Check if the media directory exists, if not, say it does not exist
if local_processor_file_status in ["0000", "0001"]:
    fetch_direct_qpu_processor_media()
    eagle_processor = f"{remote_media_dir}/media/eagle-2021-removebg.png"
    heron_processor = f"{remote_media_dir}/media/heron-2023-removebg.png"
    flamingo_processor = f"{remote_media_dir}/media/flamingo-2025-removebg.png"
    condor_processor = f"{remote_media_dir}/media/condor-2023-removebg.png"
    egret_processor = f"{remote_media_dir}/media/egret-2023-removebg.png"
    falcon_processor = f"{remote_media_dir}/media/falcon-2019-removebg.png"
    hummingbird_processor = f"{remote_media_dir}/media/hummingbird-2019-removebg.png"
    canary_processor = f"{remote_media_dir}/media/canary-2017-removebg.png"
    # For the effects images, use the URLs directly
    j_eagle_processor = f"{remote_media_dir}/media/eagle-2021-effects.png"
    j_heron_processor = f"{remote_media_dir}/media/heron-2023-effects.png"
    j_flamingo_processor = f"{remote_media_dir}/media/flamingo-2025-effects.png"
    j_condor_processor = f"{remote_media_dir}/media/condor-2023-effects.png"
    j_egret_processor = f"{remote_media_dir}/media/egret-2023-effects.png"
    j_falcon_processor = f"{remote_media_dir}/media/falcon-2019-effects.png"
    j_hummingbird_processor = f"{remote_media_dir}/media/hummingbird-2019-effects.png"
    j_canary_processor = f"{remote_media_dir}/media/canary-2017-effects.png"
elif local_processor_file_status == "1111":
    # Use the / operator to join them into a Path object and assign to variables:
    eagle_processor = local_media_dir / eagle_file_name
    heron_processor = local_media_dir / heron_file_name
    flamingo_processor = local_media_dir / flamingo_file_name
    condor_processor = local_media_dir / condor_file_name
    egret_processor = local_media_dir / egret_file_name
    falcon_processor = local_media_dir / falcon_file_name
    hummingbird_processor = local_media_dir / hummingbird_file_name
    # For the effects images, use the / operator to join them into Path objects:
    j_eagle_processor = local_media_dir / j_eagle_processor_file_name
    j_heron_processor = local_media_dir / j_heron_processor_file_name
    j_flamingo_processor = local_media_dir / j_flamingo_processor_file_name
    j_condor_processor = local_media_dir / j_condor_processor_file_name
    j_egret_processor = local_media_dir / j_egret_processor_file_name
    j_falcon_processor = local_media_dir / j_falcon_processor_file_name
    j_hummingbird_processor = local_media_dir / j_hummingbird_processor_file_name
    j_canary_processor = local_media_dir / j_canary_processor_file_name


############################################################
qcon =  rf"""
   ____   ______                                  __              
  / __ \ / ____/____   ____   ____   ___   _____ / /_ ____   _____
 / / / // /    / __ \ / __ \ / __ \ / _ \ / ___// __// __ \ / ___/
/ /_/ // /___ / /_/ // / / // / / //  __// /__ / /_ / /_/ // /    
\___\_\\____/ \____//_/ /_//_/ /_/ \___/ \___/ \__/ \____//_/     
                                                                  
🧠 Qiskit Connector® for Quantum Backend Realtime Connection
"""
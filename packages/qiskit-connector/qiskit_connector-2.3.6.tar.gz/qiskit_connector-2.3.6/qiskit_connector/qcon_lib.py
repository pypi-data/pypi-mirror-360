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
eagle_processor = f"https://github.com/QComputingSoftware/pypi-qiskit-connector/blob/main/media/eagle-2021-removebg.png"
heron_processor = f"https://github.com/QComputingSoftware/pypi-qiskit-connector/blob/main/media/heron-2023-removebg.png"
flamingo_processor = f"https://github.com/QComputingSoftware/pypi-qiskit-connector/blob/main/media/flamingo-2025-removebg.png"
condor_processor = f"https://github.com/QComputingSoftware/pypi-qiskit-connector/blob/main/media/condor-2023-removebg.png"
egret_processor = f"https://github.com/QComputingSoftware/pypi-qiskit-connector/blob/main/media/egret-2023-removebg.png"
falcon_processor = f"https://github.com/QComputingSoftware/pypi-qiskit-connector/blob/main/media/falcon-2019-removebg.png"
hummingbird_processor = f"https://github.com/QComputingSoftware/pypi-qiskit-connector/blob/main/media/hummingbird-2019-removebg.png"
canary_processor = f"https://github.com/QComputingSoftware/pypi-qiskit-connector/blob/main/media/canary-2017-removebg.png"

j_eagle_processor = f"https://github.com/QComputingSoftware/pypi-qiskit-connector/blob/main/media/eagle-2021-effects.png"
j_heron_processor = f"https://github.com/QComputingSoftware/pypi-qiskit-connector/blob/main/media/heron-2023-effects.png"
j_flamingo_processor = f"https://github.com/QComputingSoftware/pypi-qiskit-connector/blob/main/media/flamingo-2025-effects.png"
j_condor_processor = f"https://github.com/QComputingSoftware/pypi-qiskit-connector/blob/main/media/condor-2023-effects.png"
j_egret_processor = f"https://github.com/QComputingSoftware/pypi-qiskit-connector/blob/main/media/egret-2023-effects.png"
j_falcon_processor = f"https://github.com/QComputingSoftware/pypi-qiskit-connector/blob/main/media/falcon-2019-effects.png"
j_hummingbird_processor = f"https://github.com/QComputingSoftware/pypi-qiskit-connector/blob/main/media/hummingbird-2019-effects.png"
j_canary_processor = f"https://github.com/QComputingSoftware/pypi-qiskit-connector/blob/main/media/canary-2017-effects.png"

##############################################################################
qcon = f"""
   ____   ______                                  __              
  / __ \ / ____/____   ____   ____   ___   _____ / /_ ____   _____
 / / / // /    / __ \ / __ \ / __ \ / _ \ / ___// __// __ \ / ___/
/ /_/ // /___ / /_/ // / / // / / //  __// /__ / /_ / /_/ // /    
\___\_\\____/ \____//_/ /_//_/ /_/ \___/ \___/ \__/ \____//_/     
                                                                  
🧠 Qiskit Connector® for Quantum Backend Realtime Connection
"""

from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim
import ssl
import getpass
import json
import time

# print(__name__)

def display_menu(options):
    print("Menu:")
    for i, option in enumerate(options, 1):
        print(f"[{i}] {option}")

def get_json(file):
    with open(file,'r') as file:
        data = json.load(file)
    return(data)

def connect(settings):
    passwd = getpass.getpass()
    s=ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    s.verify_mode=ssl.CERT_NONE
    si= SmartConnect(host=settings["vcenter_host"], user=settings["user"], pwd=passwd, sslContext=s)
    return si

def connectionInfo(si):
    currentSession = si.content.sessionManager.currentSession
    print ("\nAgent: " + currentSession.userAgent)
    print ("Username: " + currentSession.userName)
    print ("Server: " + si.content.about.name)

def get_vm(si, name_filter=None):
    content = si.RetrieveContent()
    container = content.rootFolder  # starting point to look into
    viewType = [vim.VirtualMachine]  # object types to look for
    recursive = True  # whether we should look into it recursively
    containerView = content.viewManager.CreateContainerView(container, viewType, recursive)

    vms = containerView.view
    filtered_vms = []

    for vm in vms:
        if name_filter:
            if name_filter.lower() in vm.name.lower():
                filtered_vms.append(vm)
        else:
            filtered_vms.append(vm)

    return filtered_vms

def get_folder(si, name_filter=None):
    content = si.RetrieveContent()
    container = content.rootFolder  # starting point to look into
    viewType = [vim.Folder]  # object types to look for
    recursive = True  # whether we should look into it recursively
    containerView = content.viewManager.CreateContainerView(container, viewType, recursive)

    folders = containerView.view
    filtered_folders = []

    for folder in folders:
        if folder.childType and 'VirtualMachine' in folder.childType:
            if name_filter:
                if name_filter.lower() in folder.name.lower():
                    filtered_folders.append(folder)
            else:
                filtered_folders.append(folder)

    return filtered_folders

def get_portgroups(si, name_filter=None):
    content = si.RetrieveContent()
    container = content.rootFolder  # starting point to look into
    viewType = [vim.DistributedVirtualSwitch]  # object types to look for
    recursive = True  # whether we should look into it recursively
    containerView = content.viewManager.CreateContainerView(container, viewType, recursive)

    pgs = containerView.view
    filtered_pgs = []

    for pg in pgs:
        if name_filter:
            if name_filter.lower() in pg.name.lower():
                filtered_pgs.append(pg)
        else:
            filtered_pgs.append(pg)

    return filtered_pgs

def folder_or_vm():
    choice = input("[1] Folder\n[2] VM\nWhich item type do you want to see?: ")
    return choice

def get_folder_or_vm():
    fov = folder_or_vm()
    if(fov == "1"):
        query = input("Search a folder by name (leave blank for all):")
        folders = get_folder(content,query)
        return folders
    if(fov == "2"):
        query = input("Search a VM by name (leave blank for all):")
        vms = get_vm(si,query)
        return vms

def tweak_vm(vm, cpu, ram):
    spec = vim.vm.ConfigSpec()
    spec.numCPUs = cpu
    spec.memoryMB = ram
    # Apply the changes
    task = vm.ReconfigVM_Task(spec)
    task.info.state  # Optional: check the status of the task

def print_vm_info(vm): 
    print("================")
    print("VM Name:", vm.name) 
    print("Power State:", vm.runtime.powerState) 
    print("Number of CPUs:", str(vm.config.hardware.numCPU)) 
    print("Memory (MB):", str(vm.config.hardware.memoryMB)) 
    print("IP Address:", str(vm.guest.ipAddress))
    print("================")

def create_linked_clone(content,parent_vm,clone_name):
    clone_spec = vim.vm.CloneSpec()
    clone_spec.location = vim.vm.RelocateSpec()
    clone_spec.location.diskMoveType = vim.vm.RelocateSpec.DiskMoveOptions.createNewChildDiskBacking
    clone_spec.powerOn = False
    clone_spec.template = False

    clone_folder = content.rootFolder
    task = parent_vm.Clone(folder=clone_folder, name=clone_name, spec=clone_spec)
    
    while task.info.state == vim.TaskInfo.State.running:
        time.sleep(1)
    if task.info.state == vim.TaskInfo.State.success:
        print("Task completed successfully.")
    else:
        print(f"Task failed: {task.info.error.msg}")


    
    

    

### Connect to vCenter
settings = get_json("settings.json")   
si = connect(settings)
content = si.content
connectionInfo(si)



options = ["Search By Name", "Power On/Off VMs", "Tweak VM Performance","Create a Linked Clone of a VM", "Switch VM Network Adapter", "Create Snapshots", "Exit"]
while True:
    display_menu(options)
    choice = input("Choose an option (1-7): ")
    match choice:
        case "1": 
            query = input("Search a VM by name (leave blank for all):")
            vms = get_vm(si,query)
            print("================")
            for vm in vms:
                print_vm_info(vm)
            print("================")
        case "2":
            query = input("Search a VM by name (leave blank for all):")
            vms = get_vm(si,query)
            print("================")
            for vm in vms:
                print(vm.name)
            print("================")
            onoff = input("Do you want to turn these VMs:\n[1] On\n[2] Off ")
            check = input("Are you sure you want to change the Power State of these VMs? (y/n)")
            if check == "y" or check == "Y":
                if onoff == "1":
                    for vm in vms:
                        task = vm.PowerOn()
                        while task.info.state == vim.TaskInfo.State.running:
                            time.sleep(1)
                        if task.info.state == vim.TaskInfo.State.success:
                            print("Task completed successfully.")
                        else:
                            print(f"Task failed: {task.info.error.msg}")
                if onoff == "2":
                    for vm in vms:
                        task = vm.PowerOff()  
                        while task.info.state == vim.TaskInfo.State.running:
                            time.sleep(1)
                        if task.info.state == vim.TaskInfo.State.success:
                            print("Task completed successfully.")
                        else:
                            print(f"Task failed: {task.info.error.msg}")
            print("================")

        case "3":
            query = input("Search a VM by name (leave blank for all):")
            vms = get_vm(si,query)
            print("================")
            for vm in vms:
                print(vm.name)
            print("================")
            check = input("Are you sure you want to change the specs of these VMs? (y/n)")
            if check == "y" or check == "Y":
                cpu = int(input("How many CPUs should the VM have in total?"))
                ram = int(input("How much RAM (MB) should the VM have in total?"))
                for vm in vms:
                    task = tweak_vm(vm,cpu,ram)
                    while task.info.state == vim.TaskInfo.State.running:
                        time.sleep(1)
                    if task.info.state == vim.TaskInfo.State.success:
                        print("Task completed successfully.")
                    else:
                        print(f"Task failed: {task.info.error.msg}")
            else:
                break

        case "4":
            query = input("Search a VM by name (leave blank for all):")
            vms = get_vm(si,query)
            print("================")
            for vm in vms:
                print(vm.name)
            print("================")
            check = input("Are you sure you want to change the clone this VM? You can only clone 1 VM at a time (y/n)")
            if len(vms) == 1:
                clone_name = input("What will you name your new clone?")
                create_linked_clone(content,vms,clone_name)
            else:
                break

        case "5":
            query = input("Search a VM by name (leave blank for all):")
            vms = get_vm(si,query)
            print("================")
            for vm in vms:
                print(vm.name)
            print("================")

        case "6":
            query = input("Search a VM by name (leave blank for all):")
            vms = get_vm(si,query)
            print("================")
            for vm in vms:
                print(vm.name)
            print("================")

        case "7":
            print("Exiting...")
            exit()

        case _:
            print("Invalid choice, please select a valid option.")
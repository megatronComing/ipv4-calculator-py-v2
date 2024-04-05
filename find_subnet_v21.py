#!/usr/bin/python3
'''
Searching for a minimum subnet for every host number required out of a give IPV4 network address.
Requirements:
    ipaddress
    tabulate
By Huafeng Yu, hfyu.hzcn@gmail.com
'''
try:
    import ipaddress
except:
    print('This script depends on the third party module "ipaddress". Install it by running the following command:')
    print('( If you are using Windows, make sure that pip.exe is in the PATH environmental variable )')
    print('\tpip install ipaddress')
    exit(-1)
import os
import sys
import math

VERSION = '2.1'
ROOT = -1

def to_binary(ip_address:str) -> str:
    '''
    Converts an decimal ipv4 address to binary
    Input:
        ip_address: str, an ipv4 address without subnet mask
    Return:
        dotted ipv4 address in binary
    
    '''
    binary = bin(int(ipaddress.IPv4Address(ip_address)))
    binary = binary[2:].zfill(32)
    return '.'.join([binary[i:i+8] for i in range(0, 32, 8)])

def _subnet_details(subnet:ipaddress.IPv4Network) ->dict:
    '''
    Get detailed information about a given subnet
    获得指定子网的具体信息
    Input:
        subnet: a subnet object
    Return:
        a dictionary which contains information of the given address
    '''
    subnet_id = subnet.network_address
    subnet_id_binary = to_binary(subnet_id)
    
    hosts = list(subnet.hosts())
    first_host = hosts[0]
    first_host_binary = to_binary(first_host)

    last_host = hosts[-1]
    last_host_binary = to_binary(last_host)

    broadcast = subnet.broadcast_address
    broadcast_binary = to_binary(broadcast)

    subnet_mask = subnet.netmask
    subnet_mask_binary = to_binary(subnet_mask)

    return {
        "subnet_id": subnet_id,
        "subnet_id_bin": subnet_id_binary,
        "usable_hosts": len(hosts),
        "subnetmask": subnet_mask,
        "subnetmask_bin": subnet_mask_binary,
        "broadcast_addr": broadcast,
        "broadcast_addr_bin": broadcast_binary,
        "first_host": first_host,
        "first_host_bin": first_host_binary,
        "last_host": last_host,
        "last_host_bin": last_host_binary,
    }

def _calculate_subnets(ip:str, subnet_mask_length:int) -> list[ipaddress.IPv4Network]:
    '''
    For a given subnet, obtain its next-level subnet (two subnets, that is, the subnet mask plus 1)
    对给定子网，获取其下一级子网(两个子网, 即子网掩码加1)
    Input:
        ip: str, an ipv4 address without subnet mask
        subnet_mask_length: int, the subnet mask length
    Return:
        a list of subnet objects
    '''
    network = ipaddress.IPv4Network(f'{ip}/{subnet_mask_length}', strict=False)
    subnets = list(network.subnets())
    return subnets

def _get_subnet(ip:str, masklen:int) ->list[dict]:
    '''
    For a given subnet, obtain its next-level subnet (two subnets, that is, the subnet mask plus 1)
    对给定子网，获取其下一级子网(两个子网, 即子网掩码加1)
    Input:
        ip: str, an ipv4 address without subnet mask
        masklen: int, the subnet mask length
    Return:
        a list of dictionary, each dictionary contains information of the subnet
    '''
    if masklen > 30:
        return []
    subnets = _calculate_subnets(ip, masklen)
    result = []
    for subnet in subnets:
        details = _subnet_details(subnet)
        result.append({
            'taken': False,
            'subnet_id': str(details['subnet_id']),
            'subnet_mask_len': masklen+1,
            'subnet_mask': str(details['subnetmask']),
            'usable_hosts': details['usable_hosts'],
            'first_host': str(details['first_host']),
            'last_host': str(details['last_host']),
            'broadcast_addr': str(details['broadcast_addr'])
        })
        
    return result



class IPV4_SUBNET:
    def __init__(self, ip:str, hosts_required:list) -> None:
        '''
        Constructor
        Input:
            ip: IP address (including mask length), such as: 192.168.0.1/24
            hosts_required: A list of the number of hosts that the subnet needs to accommodate, such as: [30, 20, 5]
        Output: Print out matched subnets information
        Return: no
        
        ip: IP地址(含掩码长度), 如: 192.168.0.1/24
        hosts_required: 子网所需要容纳的主机数量列表, 如: [30, 20, 5]
        运行结果: 打印输出匹配的子网信息
        返回值: 无
        '''
        self.subnets = []
        self.hosts = sorted(hosts_required, reverse = True)
        #self.hosts_sorted = {num:self._get_max_host(num) for num in self.hosts}
        self.hosts_sorted, self.corresponding_host_bits = [], []
        for num in self.hosts:
            matched_data = self._get_max_host(num)
            if not matched_data is None:
                self.hosts_sorted.append(matched_data['max_hosts'])
                self.corresponding_host_bits.append(matched_data['host_bits'])
        
        isvalid, ipstr, masklen = self._validate_ip(ip)
        masklen = self._pre_handle_ip(ip, masklen, self.hosts)

        if isvalid:
            self.ip_addr = ipstr
            self.subnet_mask_len = masklen
        else:
            print(f'INVALID ip address {ip}, skipped.')
        self._solve_subnet(self.ip_addr, self.subnet_mask_len, ROOT)
        self._find_children()
        self._match_subnets()
        #self._print_debug_info()
        #self._print_result()
    
    def _pre_handle_ip(self, ip, masklen, hosts) -> int:
        '''
        this function is for reducing searching operations.
        make sure that it only searches the minimum host bits
        '''
        host_bits = int(math.sqrt(sum(hosts))) + 2
        return 32 - host_bits if host_bits < 32 - masklen else masklen
            

    def _print_debug_info(self) -> None:
        '''
        for debugging
        '''
        for idx, net in enumerate(self.subnets):
            print(f"{idx} {net['parent']} {net['info']['subnet_id']} {net['info']['subnet_mask_len']} {net['children']}")
        print(f'hosts required: {self.hosts}')
        print(f'hosts sorted: {self.hosts_sorted}')
        print(f'hosts bits: {self.corresponding_host_bits}')
        print('matched subnets:')
        for hosts_required,match in self.matched_subnets:
            print(f"host required:{hosts_required}\tsubnet:{match['info']['subnet_id']} masklen:{match['info']['subnet_mask_len']} first:{match['info']['first_host']} last:{match['info']['last_host']}")
    def get_formatted_result(self) -> tuple:
        '''
        return a tuple
            the first element: is the table header
            the second element: a list of tuples, each tuple stands for one row of data
        '''
        matched_count = 0
        #print(f"{len(self.matched_subnets)} subnets found out of {self.ip_addr}/{self.subnet_mask_len} for {len(self.hosts)} groups of hosts required")
        hosts, subnetid, mask, masklen, usablehosts, first, last, broadcast = [], [], [], [], [], [], [], []
        for hosts_required,match in self.matched_subnets:
            if match is None:
                hosts.append(hosts_required)
                subnetid.append('NO MATCH')
                mask.append('NA')
                masklen.append('NA')
                usablehosts.append('NA')
                first.append('NA')
                last.append('NA')
                broadcast.append('NA')
            else:
                matched_count += 1
                hosts.append(hosts_required)
                subnetid.append(match['info']['subnet_id'])
                mask.append(match['info']['subnet_mask'])
                masklen.append(match['info']['subnet_mask_len'])
                usablehosts.append(match['info']['usable_hosts'])
                first.append(match['info']['first_host'])
                last.append(match['info']['last_host'])
                broadcast.append(match['info']['broadcast_addr'])
                
        header = ['HostsNeeded', 'SubnetID', 'SubnetMask', 'MaskLen', 'UsableHosts', 'FirstHost', 'LastHost', 'BroadcastAddr']
        return (header, list(zip(hosts, subnetid, mask, masklen, usablehosts, first, last, broadcast)))
        

    def print_result(self) -> None:
        '''
        print the matched subnets
        格式化输出最终结果
        '''
        header, data = self.get_formatted_result()
        print('')
        try:
            from tabulate import tabulate
        except:
            print('This script depends on the third party module "tabulate". Install it by running the following command:')
            print('( If you are using Windows, make sure that pip.exe is in the PATH environmental variable )')
            print('\tpip install tabulate')
            exit(-1)
        print(tabulate(data, header, tablefmt='piie'))

    def get_result(self) -> list:
        result = []
        for hosts_required,match in self.matched_subnets:
            if match is None:
                result.append({'required host number': hosts_required, 'subnet matched':'NO MATCH'})
            else:
                tmp = dict(match['info'])
                del tmp['taken']
                
                result.append({'required host number': hosts_required, 'subnet matched':tmp})
        # return {'Message':f"{len(self.matched_subnets)} subnets found out of {self.ip_addr}/{self.subnet_mask_len} for {len(self.hosts)} groups of hosts required",
        #         'Result': result}
        return {'Message':f"Matching result for {self.ip_addr}/{self.subnet_mask_len}",
                'Result': result}
    
    def _get_max_host(self, host_number:int) -> dict:
        '''
        For the specified number of hosts, find the maximum number of hosts supported by the smallest subnet that supports this number, 
        which is the corresponding number of host bits in the IPV4 address.
        对跟定的主机数量, 找到支持该数量的最小子网所支持的最大主机数量即对应的在IPV4地址中的host bits数
        Input:
            host_number: int, required host number
        Ouptut:
            a dictionary
                item 'max_hosts': the minimum subnet which can accomodate hosts number of host_number
                item 'host_bits': host bits of that subnet
            returns None if no match found
        '''
        for host_bit in range(1,31):
            max_hosts_left = 2**host_bit - 2
            max_hosts_right = 2**(host_bit+1) - 2
            if max_hosts_left == host_number:
                return {'max_hosts':max_hosts_left, 'host_bits':host_bit}
            elif max_hosts_left  < host_number and max_hosts_right > host_number:
                return {'max_hosts':max_hosts_right, 'host_bits':host_bit + 1}
        print(f'FAILED to match max host number {host_number}')
        return None
    
    def _validate_ip(self, ip:str) -> tuple:
        '''
        To validate an IPv4 address
        Input:
            ip: ipv4 address with subnet mask length, e.g. 192.168.0.1/24
        Return:
            a tuple with three elements. 
            element 1: bool, to indicate whether the ip address is valid
            element 2: str, the dotted ipv4 address, all spaces removed
            element 3: int, the subnet mask length
        
        '''
        if not isinstance(ip, str):
            return (False, None, None)
        if not '/' in ip: #no subnet mask length given
            return (False, None, None)
        tmp = ip.split('/')
        ip_bytes = [byte.strip() for byte in tmp[0].split('.')]
        if len(ip_bytes) != 4:
            return (False, None, None)
        for byte in ip_bytes:
            if int(byte) < 0 or int(byte) > 255:
                return (False, None, None)
        masklen = int(tmp[1].strip())
        if masklen <= 0 or masklen >= 32:
            return (False, None, None)
        return (True,'.'.join(ip_bytes), masklen)
    
    def _solve_subnet(self, ip:str, masklen:int, parent:int) -> None:
        '''
        For a given IP address and mask, use a recursive method to find all its subnets and form a list. 
        Each element in the list records the index of the directly subordinate subnet of this subnet in this list.
        对于给定的一个IP地址和掩码, 用递归的方法找出其所有的子网,形成一个list,list中每个元素都记录了这个子网的直接上属子网在本list中的index
        Input:
            ip: str, an ipv4 address without subnet mask
            masklen: int, subnet mask length
            parent: all those found subnets belong to this parent, it is an index of self.subnets
        '''
        child_subnets = _get_subnet(ip, masklen)
        for child in child_subnets:
            idx = len(self.subnets)
            self.subnets.append({'parent':parent, 'info':child, 'children':[], 'taken':False})
            if masklen <= 31:
                self._solve_subnet(child['subnet_id'], child['subnet_mask_len'], idx)

        
    def _find_children(self) -> None:
        '''
        For the subnet list that has been established through _solve_subnet(), find the subordinate subnets of each subnet and record them.
        对于已经通过_solve_subnet()建立的的子网列表, 找到每个子网的下属子网并记录.
        '''
        for outer_idx in range(0, len(self.subnets)):
            for inner_idx in range(0, len(self.subnets)):
                if outer_idx == inner_idx:
                    continue
                if self.subnets[inner_idx]['parent'] == outer_idx:
                    self.subnets[outer_idx]['children'].append(inner_idx)
        
    def _set_subnet_status_taken(self, netidx:int) -> None:
        '''
        Mark a subnet and all its subordinates as occupied
        把子网及其所有各级的下属标记为已占用
        Input:
            netidx: int, index of self.subnets
        '''
        self.subnets[netidx]['taken'] = True
        if len(self.subnets[netidx]['children']) > 0:
            for net2 in self.subnets[netidx]['children']:
                self._set_subnet_status_taken(net2)

    def _match_subnets(self) -> None:
        '''
        Find matching subnets based on host number requirements
        根据主机数量要求, 查找匹配的子网
        '''
        self.matched_subnets = []
        for hosts, max_host_bits in zip(self.hosts,self.corresponding_host_bits):
            matched_found = False
            for host_bits in range(max_host_bits, 32 - self.subnet_mask_len):
                hosts_to_match = 2 ** host_bits - 2
                for idx, subnet in enumerate(self.subnets):
                    if not subnet['taken'] and subnet['info']['usable_hosts'] == hosts_to_match:
                        matched_found = True
                        self.matched_subnets.append((hosts,subnet))
                        self._set_subnet_status_taken(idx)
                    if matched_found:
                        break
                if matched_found:
                    break
            if matched_found:
                pass
            else:
                self.matched_subnets.append((hosts,None))
                print(f'FAILED to match subnet for host requirement {hosts}')
        
def about() -> None:
    '''
    show introduction info
    '''
    print('')
    print('-'*10 + 'IPv4 aaddress subnetting By Huafeng Yu | hfyu.hzcn@gmail.com V' + VERSION + '-'*10)
    

def usage() -> None:
    '''
    show usage
    '''
    print(f'Usage: {os.path.basename(sys.argv[0])} IP_ADDRESS/SUBNET_MASK_LEN HOST1 HOST2 HOST3 ...')
    print(f'Example: {os.path.basename(sys.argv[0])} 192.168.0.1/24 59 7 15 29 2')

def get_params( params:list ) -> tuple:
    '''
    get command line parameters
    Return:
        a tuple with two elements
            1st element: ipv4 address with subnet mask length
            2nd element: a list of host number required
        returns None if invalid command line parameters
    '''
    ip = params[0]
    hosts = [int(host) for host in params[1:]]
    return (ip, hosts)
    
def get_inputs() -> tuple:
    '''
    get command line parameters
    Return:
        a tuple with two elements
            1st element: ipv4 address with subnet mask length
            2nd element: a list of host number required
        returns None if invalid command line parameters
    '''
    if len(sys.argv) >= 3:
        return get_params(sys.argv[1:])
        #ip = sys.argv[1]
        #hosts = [int(host) for host in sys.argv[2:]]
        #return (ip, hosts)
    else:
        return None

if __name__=='__main__':
    about()
    user_input = get_inputs()
    if user_input is None:
        usage()
    else:
        subnets = [user_input]
        for ip, hosts in subnets:
            myip = IPV4_SUBNET(ip, hosts)
            myip.print_result()
            
    

> Ray Cluster对数据进行预处理，提高任务并行

> 原始数据MapReduce全排序

> 数据分箱，hex(16进制)分箱

### 用户查询

![img](https://tva1.sinaimg.cn/large/008vxvgGly1h7qsxhm3jsj30mj06hglr.jpg)

### 数据预处理

![1280X1280](https://tva1.sinaimg.cn/large/008vxvgGly1h7qszwpmzbj30e80hymxh.jpg)





### 数据预处理（集群）

### 排序

#### MapReduce 全排序

![1280X1280 (1)](https://tva1.sinaimg.cn/large/008vxvgGly1h7qt2r9nqcj30840b7glw.jpg)



- 方法一：map任务单独排序，通过reduce进行总排序，并行度不高，无法分布式计算特点，不推荐。

- 方法二：针对方法一进行改进
   1. 使用多个partition对map结果进行区间分区，将多个分区结果拼接，得到一个全局排序文件

      ![0f8a6752-8d1b-4e4b-9ebf-8dbbc634bf16](https://miro.medium.com/max/640/1*nJYIs2ktVkqVsgSUCzfjaA.gif)

      

      
   
   2. *对具有 4 个分区的分布式数据集进行混洗，其中每个分区是一组 4 个块。例如，在排序操作中，每个方格都是一个排序后的子分区，其键位于不同的范围内。然后每个 reduce 任务对相同阴影的子分区进行合并排序。*
   
      参考：<https://medium.com/distributed-computing-with-ray/executing-a-distributed-shuffle-without-a-mapreduce-system-d5856379426c>

### 数据分箱（分桶） 

> 原始数据 -> 数据分片 Shared （理想情况分到对应的桶里TODO）->db文件

#### 简介

- 数据分箱（也称为离散分箱或分段）是一种数据预处理技术，用于减少次要观察误差的影响，是一种将多个连续值分组为较少数量的“分箱”的方法。

#### 分箱方法

- #####  有监督分箱准备：预先设定一个阈值，分箱基准初始化：根据要离散的属性对实例进行排序，每个实例属于一个区间合并： 符合同一基准特征的实例进行合并

- #####  无监督分箱  等距分箱： 从最小值到最大值之间,均分为 N 等份, 这样, 如果 A,B 为最小最大值, 则每个区间的长度为 W=(B−A)/N , 则区间边界值为A+W,A+2W,….A+(N−1)W 。这里只考虑边界，每个等份里面的实例数量可能不等。  等频分箱：区间的边界值要经过选择,使得每个区间包含大致相等的实例数量。比如说 N=10 ,每个区间应该包含大约10%的实例

#### 名词解释

- |      | 定义      | 解释   | 说明                                   |
     | ---- | --------- | ------ | -------------------------------------- |
     | 1    | BucketLen | 桶大小 | 桶的额定容量，每个桶最多存储的数据条目 |
     | 2    | BucketNum | 桶数量 | 桶的额定数量                           |

#### 分桶规则

- 按照hash之后的item字节位数匹配进行分桶，可容纳数据条数 .桶大小和桶数量的乘积刚好是$$$$2^8*16 $$$$，即：$$$$BucketNum* BucketLen = 2^8*16 $$$$

- 每个桶的额定容量设定取固定值，
     1. 假设依次为16的幂次递增，即：16，256， 4096， 65536 ……
     2. 假设依次为2^8的幂次递增

- 桶的数量随着桶的容量增加递减

- 文件存储：Item长度为16字节，文件夹最大可按照2个字节位拆分，每个文件夹下至多存放 2*2^8 （2^16）个文件夹，按照树形结构拆分
     1. 文件大小=桶大小

     2. 叶子节点文件夹包含文件数量为256（ 65536 / 文件大小）

        *结构1：假设每个父文件夹最多包含256个文件夹（按照1个字节划分，每个字节8位，2^8）*

     ![1280X1280 (2)](https://tva1.sinaimg.cn/large/008vxvgGly1h7qt4oadyqj30dr0iogmo.jpg)

      

     *结构2：假设每个父文件夹最多包含2^8^2(65536)个文件夹，文件夹深度减半，注意叶子节点文件夹数量仍为256。*

#### 分桶实现过程

- 读取数据集

     ```Python
     ds = ray.data.read_*(paths=[data_path], **{}).repartition(200)
     ```

- 将数据集排序列进行hash，结果使用16进制表示，新增 hash_item 列

     ```Python
     from hashlib import blake2b
     
     blake2b(str.encode("iajjvfDousbMDlbYcEIqTwYhkqJuLMnmNzvDlkTShnZakcKstAEDfZXRLehdqRNn"), digest_size=16).hexdigest()
     Out[*]:
     '06a8ad89dfe8a43e036040dcf8f128ff' 
      
     len('06a8ad89dfe8a43e036040dcf8f128ff')
     Out[*]:
     32
     
      
     ```

- 将数据进行hash排序

- 分箱配置，按照16进制位数（SEVERAL）进行分享，桶个数（n_bucket = 16 ** SEVERAL）

- 动态得到分箱基准`bin`

     ```Python
     bins = [bin for bin in range(1, n_bucket)]
     
     def get_bin(self, i):
        if len(hex(i)[2:]) == self.several:
            bin = hex(i)[2:]
        else:
            bin = f"{'0'*(self.several-len(hex(i)[2:]))}{hex(i)[2:]}"
        print("bin: ", bin)
        return bin
     ```

- 遍历整个数列，按照公式 str(hash_item[:SEVERAL]) == bucket_name, 将item放入对应的桶中

- 对放在同一个桶中的数据进行apsi加密

Ray Map Reduce

```Python
@ray.remote
def map(data, npartitions):
    outputs = [list() for _ in range(npartitions)]
    for row in data:
        # int(int("ff", 16)/0xff)
        index = int(int(row["hash_item"][:30], 16)/ npartitions) 
        print("index: ", index)
        outputs[index].append(row)
    return outputs

@ray.remote
def reduce(*partitions):
    print("partitions")
    # Flatten and sort the πpartitions.
    # return sorted(row for partition in partitions for row in partition)
    # TODO
    
npartitions = 16**30
dataset = ds
print(npartitions)
map_outputs = [
    map.remote(partition, npartitions) for partition in dataset
]
```

受限于数组长度：

npartitions = 16**30

```Python
import sys
maxsize = sys.maxsize
print(maxsize)
print(str(hex(maxsize)))


# 9223372036854775807
# 0x7fffffffffffffff
```

##### Ray Tree of Actor

Supervisor Actor 预先定义分桶；

Worker Actor 执行具体的任务，对分桶数据进行处理，APSI加密。



![006f1c4b-8d4b-4da8-bf58-6e2b52a34316](https://tva1.sinaimg.cn/large/008vxvgGly1h7qt6xi8vvj30ch06b3ym.jpg)



Example：

```Python
@ray.remote(num_cpus=1)
class Worker:
    def work(self):
        return "done"

@ray.remote(num_cpus=1)
class Supervisor:
    def __init__(self):
        self.workers = [Worker.remote() for _ in range(3)]
    def work(self):
        return ray.get([w.work.remote() for w in self.workers])

ray.init()
sup = Supervisor.remote()
print(ray.get(sup.work.remote()))  # outputs ['done', 'done', 'done']
```

##### 测试记录

单机插入256：

![2ea4ed11-c83f-48cc-bd79-fac144fe8b20](https://tva1.sinaimg.cn/large/008vxvgGly1h7qt583no3j30tf0bkdje.jpg)



单机10w插入：

![img](https://tva1.sinaimg.cn/large/008vxvgGly1h7qsxl0dk4j30ys0c943e.jpg)	

加密10w 单机

![629bee89-a4bf-442f-b673-ee73a04fc1ea](https://tva1.sinaimg.cn/large/008vxvgGly1h7qt5i5rl3j30tj0fmdju.jpg)



#### Test Case

> 用例说明：
>
> 1. APSI Client查询 "JRIKrInSyZfcBADbXigLiGnHisxpWrEctHEQzrryFjAHFoPQAjEoxQhTPoYgXIFI"
> 2. Hash value: "f181eec872a70a509d10d9aa4ec74baf"
> 3. 命中Bucket， 即db文件 apsi_fi.db
> 4. APSI server 从db文件load_db
> 5. APSI client 发起query请求
> 6. `assert query result == {"JRIKrInSyZfcBADbXigLiGnHisxpWrEctHEQzrryFjAHFoPQAjEoxQhTPoYgXIFI": "GukbcSbVKQheaIWdNCSszRGwWEJAWTSOPfeTyHqomeCwPehKZHUEugDMxyXtaJHg"}`

Apsi db:

暂时无法在飞书文档外展示此内容

Query csv:

Test code Python:  <https://gitlab.openmpc.com/openmpc/pyapsi/-/blob/develop/examples/example_query_from_bucket.py>

APSI SERVER:

max_label_length=64

Params String:

```Python
# parameters/256M-1.json

params_string = """{
    "table_params": {
        "hash_func_count": 1,
        "table_size": 1638,
        "max_items_per_bin": 8100
    },
    "item_params": {
        "felts_per_item": 5
    },
    "query_params": {
        "ps_low_degree": 310,
        "query_powers": [ 1, 4, 10, 11, 28, 33, 78, 118, 143, 311, 1555]
    },
    "seal_params": {
        "plain_modulus_bits": 22,

        "poly_modulus_degree": 8192,
        "coeff_modulus_bits": [ 56, 56, 56, 32 ]
    }
}
# 100k-1
{
    "table_params": {
        "hash_func_count": 1,
        "table_size": 409,
        "max_items_per_bin": 20
    },
    "item_params": {
        "felts_per_item": 5
    },
    "query_params": {
        "ps_low_degree": 0,
        "query_powers": [ 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20 ]
    },
    "seal_params": {
        "plain_modulus": 65537,
        "poly_modulus_degree": 2048,
        "coeff_modulus_bits": [ 48 ]
    }
}
```

10w:

python3 tools/scripts/test_data_creator.py 100000 1 1 64 64

联调测试：

ssh -p 37928 [primihub@118.190.39.100](mailto:primihub@118.190.39.100)

Csv path: /home/apsidata/

DB path: /home/apsidb/

10w:

CSV path: /home/apsidata/db_10w.csv

10w: /home/apsidb/10w/apsidb

100w:

CSV path: /home/apsidata/db_100w.csv

DB path: /home/apsidb/100w/apsidb/

## Ray Clusters

[docs.ray.io](https://docs.ray.io/en/latest/cluster/kubernetes/getting-started.html)

[Environment Dependencies — Ray 2.0.1](https://docs.ray.io/en/latest/ray-core/handling-dependencies.html)

使用ray集群执行数据预处理

> 在集群上运行时，一个常见的问题是 Ray 期望这些“依赖关系”存在于每个 Ray 节点上。如果这些不存在，您可能会遇到诸如 等`ModuleNotFoundError`问题`FileNotFoundError`。
>
> [为了解决这个问题，您可以 (1) 使用 Ray Cluster Launcher](https://docs.ray.io/en/latest/cluster/vms/getting-started.html#vm-cluster-quick-start)提前准备好对集群的依赖项

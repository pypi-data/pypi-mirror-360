import asyncio
from typing import Iterable
import traceback
import warnings
import subprocess
try:
    from tqdm import tqdm
except ModuleNotFoundError:
    subprocess.check_call(['pip','install', "tqdm"])
    from tqdm import tqdm
    
async def _taskRun(funcd, jder:tqdm, sem:asyncio.Semaphore):
    async with sem:
        err = None
        try:
            result = await funcd
        except:
            err = traceback.format_exc()
            result = None
            warnings.warn(err)
    jder.update(1)
    return result, err
    

async def taskRun(aync_func, datas:Iterable, num:int, **ceil_kwargs):
    jder = tqdm(datas)
    sem = asyncio.Semaphore(num) 
    res = await asyncio.gather(*[_taskRun(aync_func(data, **ceil_kwargs), jder, sem) for data in datas])
    jder.close()
    errnum=0
    results = []
    for result, err in res:
        results.append(result)
        if err: errnum+=1
    print(f'完成数: {len(datas)-errnum}/{len(datas)}')
    return results
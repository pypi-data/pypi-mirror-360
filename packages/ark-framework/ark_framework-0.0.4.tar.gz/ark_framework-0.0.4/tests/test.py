from ark.asynco import Asynco, asynco


@asynco(pool_name='God')
def test(sts):
    print('Hello Start {0}'.format(sts))
    import time
    time.sleep(5)
    print('Hello End {0}'.format(sts))

Asynco.create_pool('God',size=3)

test('1')
test('2')
test('3')
test('4')
test('5')
test('6')
test('7')
test('8')
test('9')
Asynco.complete_all_task(pool_name='God')
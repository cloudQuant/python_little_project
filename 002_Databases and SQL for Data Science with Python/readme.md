df = pd.read_sql_query("select * from instructor;", conn)
这个函数用的比较少，后期如果用到数据库，可以考虑尝试一下。


ACID机制值得学习：
```
DELIMITER //
CREATE PROCEDURE TRANSACTION_JAMES()
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;
    START TRANSACTION;
    UPDATE BankAccounts
    SET Balance = Balance-1200
    WHERE AccountName = 'James';
    UPDATE BankAccounts
    SET Balance = Balance+1200
    WHERE AccountName = 'Shoe Shop';
    UPDATE ShoeShop
    SET Stock = Stock-4
    WHERE Product = 'Trainers';
    UPDATE BankAccounts
    SET Balance = Balance-150
    WHERE AccountName = 'James';
    COMMIT;
END //
DELIMITER ; 
```
from airflow.operators.postgres_operator import PostgresOperator
from airflow.hooks.postgres_hook import PostgresHook
from airflow.operators.python import PythonOperator
from airflow import DAG
from airflow.utils.task_group import TaskGroup
from datetime import datetime, timedelta
import psycopg2 
import sqlalchemy

from functions import *



engine = sqlalchemy.create_engine('postgresql+psycopg2://postgres:postgres@localhost/customers')


default_args = {
    'start_date': datetime(2022, 6, 19)
}

with DAG(dag_id='sales',
         default_args=default_args,
         schedule_interval='@daily',
         catchup=False,
         tags=['currency']
         ) as dag:


    t1 = PythonOperator(
        task_id='extract_data',
        python_callable=extract,
        do_xcom_push=False,
        dag=dag,
    )

    # aplicar transformações na tabela
    t2 = PythonOperator(
        task_id='transforma_tabela',
        python_callable=transform,
        do_xcom_push=False,
        dag=dag,
    )

    with TaskGroup('create_tables_stages') as create_tables_stages:
        # cria tabela
        s1 = PostgresOperator(
            task_id='criar_Stage_Customers',
            postgres_conn_id='postgres',
            sql=r"""
                CREATE TABLE IF NOT EXISTS stg_customers (
                customernumber INT NOT NULL,                 
                customername VARCHAR(30) NOT NULL,
                contactlastname VARCHAR(30) NOT NULL,
                contactfirstname VARCHAR(30) NOT NULL,
                phone VARCHAR(30) NOT NULL,
                addressline1 VARCHAR(30) NOT NULL,
                city VARCHAR(30) NOT NULL,
                state VARCHAR(20) NOT NULL,
                postalcode VARCHAR(30) NOT NULL,
                country VARCHAR(30) NOT NULL,
                creditlimit FLOAT NOT NULL
                )
            """,
            dag=dag,
        )

         # cria tabela
        s2 = PostgresOperator(
            task_id='criar_Stage_Products',
            postgres_conn_id='postgres',
            sql=r"""
                CREATE TABLE IF NOT EXISTS stg_products (
                productcode VARCHAR(40) NOT NULL,
                productname VARCHAR(40) NOT NULL,
                productline VARCHAR(20) NOT NULL,
                productvendor VARCHAR(25) NOT NULL,
                productdescription VARCHAR(200) NOT NULL
                )
            """,
            dag=dag,
        )

         # cria tabela
        s3 = PostgresOperator(
            task_id='criar_Stage_Time',
            postgres_conn_id='postgres',
            sql=r"""
                CREATE TABLE IF NOT EXISTS stg_time (
                ordernumber INT NOT NULL,               
                orderdate date NOT NULL,
                requireddate date NOT NULL,
                shippedDate date
                    )
            """,
            dag=dag,
        )

      
         # cria tabela
        s4 = PostgresOperator(
            task_id='criar_Stage_Employees',
            postgres_conn_id='postgres',
            sql=r"""
                CREATE TABLE IF NOT EXISTS stg_emp (
                employeenumber INT NOT NULL,                        
                lastname VARCHAR(30) NOT NULL,
                firstname VARCHAR(30) NOT NULL,
                email VARCHAR (40) NOT NULL,
                reportsto VARCHAR (50) NOT NULL,
                jobtitle VARCHAR(30) NOT NULL
                )
            """,
            dag=dag,
        )

        s5 = PostgresOperator(
            task_id='criar_Stage_Orderd',
            postgres_conn_id='postgres',
            sql=r"""
                CREATE TABLE IF NOT EXISTS stg_orderd (
                id_ordd SERIAL PRIMARY KEY, 
                ordernumber int not null,
                orderLineNumber int not null,
                status VARCHAR(20) not null
                )
            """,
            dag=dag,
        )

         # cria tabela
        s6 = PostgresOperator(
            task_id='criar_Stage_Fato',
            postgres_conn_id='postgres',
            sql=r"""
                CREATE TABLE IF NOT EXISTS stg_fato (
                id_fato SERIAL PRIMARY KEY,     
                customername VARCHAR(30) NOT NULL,    
                productname VARCHAR(40) NOT NULL,    
                orderdate date NOT NULL,
                requireddate date NOT NULL,        
                lastname VARCHAR(30) NOT NULL,    
                quantityordered int NOT NULL,
                priceeach float NOT NULL,
                buyprice float NOT NULL
                )
            """,
            dag=dag,
        )

    t3 = PythonOperator(
        
        task_id='load_stages',
        python_callable=load_stage,
        do_xcom_push=False,
        dag=dag,
    )

    with TaskGroup('create_tables_tasks') as create_tables_tasks:
        # cria tabela
        d1 = PostgresOperator(
            task_id='criar_DM_Customers',
            postgres_conn_id='postgres',
            sql=r"""
                CREATE TABLE IF NOT EXISTS dm_customers (
                id_customers SERIAL PRIMARY KEY,
                customernumber INT NOT NULL,    
                customername VARCHAR(50) NOT NULL,
                contactlastname VARCHAR(50) NOT NULL,
                contactfirstname VARCHAR(50) NOT NULL,
                phone VARCHAR(50) ,
                addressline1 VARCHAR(50) ,
                city VARCHAR(50) ,
                state VARCHAR(50),
                postalcode VARCHAR(50) ,
                country VARCHAR(50) ,
                creditlimit FLOAT 
                )
            """,
            dag=dag,
        )

         # cria tabela
        d2 = PostgresOperator(
            task_id='criar_DM_Products',
            postgres_conn_id='postgres',
            sql=r"""
                CREATE TABLE IF NOT EXISTS dm_products (
                id_products SERIAL PRIMARY KEY,
                productcode VARCHAR(40) NOT NULL,    
                productname VARCHAR(50) NOT NULL,
                productline VARCHAR(40) NOT NULL,
                productvendor VARCHAR(40)NOT NULL,
                productdescription VARCHAR(1000) NOT NULL
                )
            """,
            dag=dag,
        )

         # cria tabela
        d3 = PostgresOperator(
            task_id='criar_DM_Time',
            postgres_conn_id='postgres',
            sql=r"""
                CREATE TABLE IF NOT EXISTS dm_time (
                id_time SERIAL PRIMARY KEY,  
                ordernumber INT NOT NULL,   
                orderdate date NOT NULL,
                requireddate date NOT NULL,
                shippedDate date
                    )
            """,
            dag=dag,
        )

      
         # cria tabela
        d4 = PostgresOperator(
            task_id='criar_DM_Employees',
            postgres_conn_id='postgres',
            sql=r"""
                CREATE TABLE IF NOT EXISTS dm_emp (
                id_emp SERIAL PRIMARY KEY, 
                employeenumber INT NOT NULL,   
                lastname VARCHAR(50) NOT NULL,
                firstname VARCHAR(50) NOT NULL,
                email VARCHAR (50) NOT NULL,
                reportsto VARCHAR (50) NOT NULL,
                jobtitle VARCHAR(50) NOT NULL
                )
            """,
            dag=dag,
        )

        s5 = PostgresOperator(
            task_id='criar_DM_orderd',
            postgres_conn_id='postgres',
            sql=r"""
                CREATE TABLE IF NOT EXISTS dm_orderd (
                id_ordd SERIAL PRIMARY KEY, 
                ordernumber INT NOT NULL,                     
                orderLineNumber int not null,
                status VARCHAR(20) not null
                )
            """,
            dag=dag,
        )
    
    t4 = PythonOperator(
        
        task_id='extract_to_DMs',
        python_callable=extract_to_DMs,
        do_xcom_push=False,
        dag=dag,
    )

    t5 = PythonOperator(
        
        task_id='load_DMs',
        python_callable=load_DMs,
        do_xcom_push=False,
        dag=dag,
    )

             # cria tabela
    t6 = PostgresOperator(
        task_id='criar_Fato',
        postgres_conn_id='postgres',
        sql=r"""
            CREATE TABLE IF NOT EXISTS fato (
            id_sales SERIAL PRIMARY KEY,
            id_customers INT NOT NULL ,
            id_products INT NOT NULL,
            id_time INT NOT NULL,
            id_emp INT NOT NULL,
            id_ordd INT NOT NULL,
            CONSTRAINT fk_customers FOREIGN KEY (id_customers) REFERENCES dm_customers(id_customers),
            CONSTRAINT fk_products FOREIGN KEY (id_products) REFERENCES dm_products (id_products),
            CONSTRAINT fk_time FOREIGN KEY (id_time) REFERENCES dm_time(id_time),
            CONSTRAINT fk_emp FOREIGN KEY (id_emp) REFERENCES dm_emp(id_emp),
            CONSTRAINT fk_ordd FOREIGN KEY (id_ordd) REFERENCES dm_orderd(id_ordd),
            quantityordered int NOT NULL,
            priceeach float NOT NULL,
            buyprice float NOT NULL
            )
            """,
            dag=dag,
        )

    t7 = PythonOperator(
        
        task_id='load_fato',
        python_callable=load_Fato,
        do_xcom_push=False,
        dag=dag,
    )

    # dependências entre as tarefas
    t1 >> t2 >> create_tables_stages >> t3 >> create_tables_tasks >> t4 >> t5 >> t6 >> t7





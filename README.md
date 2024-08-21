[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)

# PROD-Bobiki-Back

### ! All endpoints have prefix "/api/v1"

### 1. GET /products

Эндпоинт, который отвечает за возврат всех существующих в компании продуктов, для дальнейшего выбора их заказчиком(-и).
```json
{
  "products": [
    {
      "id": 1,
      "name": "{some_name}",
      "time": 10
    },
    {
      "id": 2,
      "name": "{other_name}",
      "time": 10
    }
  ]
}
```

### 2. GET /products/<int: product_id>/documents

Эндпоинт, который возвращает список документов по id продукта, необходимых для оформления продукта
```json
{
  "product": "product_name",
  "documents": [
    "document_name",
    "document_name"
  ]
}
```

### 3. GET /current_user

Эндпоинт, который возвращает текущего юзера, находящегося на странице  
**_! Так как считается, что приложение работает в экосистеме банка, эндпоинт возвращает первого пользователя из БД_**

```json
{
  "user": {
    "id": 1,
    "name": "Имя",
    "surname": "Фамилия",
    "middle_name": "Отчество",
    "phone_number": "71234567891"
  }
}
```

### 4. POST /meetings/create
Запрос на создание встречи с заказчиком. Должен содержать всю информацию о предстоящей встрече

```json
{
  "user": {
    "id": 1,
    "name": "Имя",
    "surname": "Фамилия",
    "middle_name": "Отчество",
    "phone_number": "71234567891"
  },
  "meeting": {
    "start_datetime": "2024-04-01 11:30",
    "place": "address"
  },
  "additional_users": [
    {
      "name": "Криштиану",
      "surname": "Роналду",
      "middle_name": "Мессиевич",
      "role": "role",
      "passport_data": "{серия} {номер}",
      "phone_number": "71234567891"
    }
  ],
   "products": [
      {
        "name": "{some_name}"
      },
      {
        "name": "{other_name}"
      } 
   ]
}

```
Ответом от сервера будет 
```json
{
  "status": "some message, depending on status code"
}
```


### 5. GET /user/meetings/<int: meeting_id>

Эндпоинт, возвращающий данные о встрече с заказчиком

```json
{
  "user": {
    "id": 1,
    "name": "Имя",
    "surname": "Фамилия",
    "middle_name": "Отчество",
    "phone_number": "71234567891"
  },
  "meeting": {
    "start_datetime": "2024-04-01 11:30",
    "end_datetime": "2024-04-01 12:30",
    "place": "address"
  },
  "courier": {
    "name": "Vladimir",
    "surname": "Putin",
    "middle_name": "Vladimirovich",
    "phone_number": "71234567891"
  },
  "additional_users": [
    {
        "id": 1,
        "name": "name",
        "surname": "surname",
        "middle_name": "middle name",
        "role": "role",
        "passport_data": "6020 878254",
        "phone_number": "75852478965"
      },
    {
        "id": 2,
        "name": "name",
        "surname": "surname",
        "middle_name": "middle name",
        "role": "role",
        "passport_data": "6020 878254",
        "phone_number": "75852478965"
      }
  ],
  "products": [
    {
      "id": 1,
      "name": "{some name}",
      "time": 60
    },
    {
      "id": 2,
      "name": "{other name}",
      "time": 30
    }
  ]
}
```

### 6. GET /user/meetings/all 

Метод возвращающий все назначенные встречи заказчика. В ответе содержится вся информация о встрече(информация о самой встрече, информация о курьере, документы)
```json
{
  "1": {
      "user": {
        "id": 1,
        "name": "Имя",
        "surname": "Фамилия",
        "middle_name": "Отчество",
        "phone_number": "71234567891"
      },
    "meeting": {
      "start_datetime": "2024-04-01 11:30",
      "end_datetime": "2024-04-01 12:30",
      "place": "address"
    },
    "courier": {
      "name": "Vladimir",
      "surname": "Putin",
      "middle_name": "Vladimirovich",
      "phone_number": "71234567891"
    },
    "additional_users": [
      {
        "id": 1,
        "name": "name",
        "surname": "surname",
        "middle_name": "middle name",
        "role": "role",
        "passport_data": "6020 878254",
        "phone_number": "75852478965"
      },
      {
        "id": 2,
        "name": "name",
        "surname": "surname",
        "middle_name": "middle name",
        "role": "role",
        "passport_data": "6020 878254",
        "phone_number": "75852478965"
      }
    ],
    "products": [
    {
      "id": 1,
      "name": "{some name}",
      "time": 60
    },
    {
      "id": 2,
      "name": "{other name}",
      "time": 30
    }
  ]
  },
  "2": {
    "user": {
        "id": 1,
        "name": "Имя",
        "surname": "Фамилия",
        "middle_name": "Отчество",
        "phone_number": "71234567891"
    },
    "meeting": {
      "start_datetime": "2024-04-01 11:30",
      "end_datetime": "2024-04-01 12:30",
      "place": "address"
    },
    "courier": {
      "name": "Vladimir",
      "surname": "Putin",
      "middle_name": "Vladimirovich",
      "phone_number": "71234567891"
    },
    "additional_users": [
      {
        "id": 1,
        "name": "name",
        "surname": "surname",
        "middle_name": "middle name",
        "role": "role",
        "passport_data": "6020 878254",
        "phone_number": "75852478965"
      },
      {
        "id": 2,
        "name": "name",
        "surname": "surname",
        "middle_name": "middle name",
        "role": "role",
        "passport_data": "6020 878254",
        "phone_number": "75852478965"
      }
    ],
    "products": [
    {
      "id": 1,
      "name": "{some name}",
      "time": 60
    },
    {
      "id": 2,
      "name": "{other name}",
      "time": 30
    }
  ]
  }
}
```

### 7. PATCH /meetings/<int: meeting_id>

Запрос на изменение данных встречи
Ожидаемый json запроса:   
#### Поля могут быть пропущены, если их изменение не требуется
```json
{
  "additional_users": [
    {
      "id": 1,
      "name": "name",
      "surname": "surname",
      "middle_name": "middle name",
      "role": "role",
      "passport_data": "6020 878254",
      "phone_number": "75852478965"
    },
    {
      "id": 2,
      "name": "name",
      "surname": "surname",
      "middle_name": "middle name",
      "role": "role",
      "passport_data": "6020 878254",
      "phone_number": "75852478965"
    }
  ],
  "start_datetime": "2024-11-22 15:30",
  "products": [
    {
      "name": "{some name}"
    },
    {
      "name": "{other name}"
    }
   ],
  "place": "address"
}
```

Возвращаем 

```json
{
  "message": "success edit"
}
```

### 8. GET /meetings/free_time/<str: date>/<int: length>

Эндпоинт, возвращающий свободные time-слоты в данный день для встречи определённой длительности

```json
{
  "free_slots": [
    "2024-01-04 15:00",
    "2024-01-04 15:30"
  ]
}
```

### 9. DELETE /meetings/<int: meeting_id>

Удаление одной из встреч пользователя без возможности восстановления

```json
{
  "message": "some message, depending on status code"
}
```

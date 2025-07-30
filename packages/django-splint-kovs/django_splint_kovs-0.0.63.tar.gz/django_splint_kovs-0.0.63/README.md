# django-splint-kovs
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/django-splint-kovs)
![PyPI - License](https://img.shields.io/pypi/l/django-splint-kovs)
![PyPI](https://img.shields.io/pypi/v/django-splint-kovs)
<br>

django-splint-kovs is a tool for projects with django framework, here you will find some basic settings for your models, views, serializers and adminitrators. This package assumes you have already started a project with django framework, otherwise see [Getting started with Django](https://www.djangoproject.com/start/)

## How to install?
```python

pip install django-splint-kovs

```

## Features

- SplintViewSet (Splint version of DRF GenericViewSet):
- SplintModelViewSet (Splint version of DRF ModelViewSet)

  This a simple class to django views, you can use it by simply inheriting it in your views.
  ```
  class StudentViewSet(SplintViewSet, ...):
  ```

  with this you have set some custom attributes to the class, for example:

  ```
  class StudentViewSet(SplintViewSet, ...):
    serializer_class = StudentSerializer # serializer default
    # Custom serializers
    read_serializer_class = StudentRetrieveSerializer # serializer to retrieve action
    list_serializer_class = StudentListSerializer # serializer to list action 
    write_serializer_class = StudentWriteSerializer # serializer to create, destroy and update actions
  ```
  
  
- SplintModel:

  This class is an example base model, it contains some generic attributes that can be very useful, such as fields that save the creation, update and deletion date of records. With that, we don't need to worry about creating these fields manually for each of our models.

  Another utility: 
  
  - Overriding of the delete method to ensure that objects are not completely deleted.
  - Saves original value model fields with pattern `__original_{field_name}` in local cache before any actions (save, deleted) as also signals flow.
  - Log activity to every action in the system

  Usage:
  ```
  class StudentModel(SplintModel):
    name: ..
  
  Student.objects.create(name='first student')
  # Student fields
  {
    id: 1,
    name: 'first student',
    created_at: <DateTime>,
    updated_at: <DateTime>,
    _deleted: False,
    _deleted_at: <Datetime>
  }
  
  students = Student.objects.all()
  students.delete() # this objects has not been deleted completely, it will only be invisible to objects manage default.
  
  s_with_deleted = Student.objects_with_deleted.filter(_deleted=True) # list of "deleted" students.

  ```

- SplintImageField:

  This class provide image width, height (at least one dim) and quality to resize image using PIL. Vertical crop images will be applied before resizing the image, you can use it by simply seting in your models fields.
  
  ```
  class StudentModel(SplintModel):
    profile_picture = SplintImageField('Profile picture', upload_to='student', width=120, ...)
    ...
  ```
  
- splint_cached_property:

  This class a sample decorator for saves properties values in cache services, for details on how to configure access to topics cache in django docs
  https://docs.djangoproject.com/en/4.0/topics/cache/

  ```
  class StudentModel(SplintModel):
  ...
  
  def studentgroups_actives__cache_key(self):
    return sha224(f'{self.id}'.encode()).hexdigest()
  
  @splint_cached_property
  def studentgroups_actives(self):
    ...

  ```
  
  by default this class will look for a function with pattenr `{property_name}__cache_key` that returns a text representing a key, this key will be used to retrieve the value later.

## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE` for more information.

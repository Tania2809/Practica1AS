app.controller("categoriasCtrl", function ($scope, $http) {
    $scope.categorias = [];
    $scope.mostrarTodos = true;
    
    // Inicializar el bus de eventos
    const eventBus = {
        subscribers: {},
        
        // Suscribirse a eventos
        subscribe: function(eventName, callback) {
            if (!this.subscribers[eventName]) {
                this.subscribers[eventName] = [];
            }
            this.subscribers[eventName].push(callback);
        },
        
        // Publicar eventos
        publish: function(eventName, data) {
            if (this.subscribers[eventName]) {
                this.subscribers[eventName].forEach(callback => {
                    callback(data);
                });
            }
        }
    };

    // Servicio de Categorías - Escucha eventos
    const categoriaService = {
        cargarTodas: function() {
            $http.get("/categorias/all").then(function(res) {
                $("#tablaCategorias").html(res.data);
                eventBus.publish('categorias_actualizadas', res.data);
            });
        },
        
        buscar: function(nombre) {
            $http.get("/categorias/buscar", {
                params: { busqueda: nombre }
            }).then(function(response) {
                $("#tablaCategorias").html(response.data);
                eventBus.publish('busqueda_realizada', response.data);
            });
        },
        
        guardar: function(categoria) {
            return $http.post("/categorias/agregar", categoria);
        }
    };

    // Servicio de Notificaciones - Reacciona a eventos
    const notificacionService = {
        init: function() {
            eventBus.subscribe('categoria_guardada', function(data) {
                console.log('Notificación: Categoría guardada exitosamente', data);
            });
            
            eventBus.subscribe('error_guardado', function(error) {
                console.error('Notificación: Error al guardar categoría', error);
            });
        }
    };

    // Servicio de Analytics - Reacciona a eventos
    const analyticsService = {
        init: function() {
            eventBus.subscribe('busqueda_realizada', function(data) {
                console.log('Analytics: Búsqueda realizada', data);
            });
            
            eventBus.subscribe('categoria_guardada', function(data) {
                console.log('Analytics: Nueva categoría creada', data);
            });
        }
    };

    // Inicializar servicios
    notificacionService.init();
    analyticsService.init();

    // Inicializar Pusher para eventos en tiempo real
    Pusher.logToConsole = true;
    var pusher = new Pusher("db840e3e13b1c007269e", { cluster: 'us2' });
    var channel = pusher.subscribe("canalCategorias");
    
    channel.bind("eventoCategorias", function(data) {
        if ($scope.mostrarTodos) {
            eventBus.publish('evento_externo', data);
            categoriaService.cargarTodas();
        }
    });

    // Cargar datos iniciales
    categoriaService.cargarTodas();
    $scope.mostrarTodos = true;

    // Guardar categoría - Publica evento en lugar de llamada directa
    $scope.guardar = function(categoria) {
        categoriaService.guardar(categoria)
            .then(function(response) {
                eventBus.publish('categoria_guardada', response.data);
                $scope.categoria = {};
                categoriaService.cargarTodas();
            })
            .catch(function(err) {
                eventBus.publish('error_guardado', err);
            });
    };

    // Buscar categorías - Publica evento
    $scope.buscar = function(nombre) {
        if (!nombre || nombre.trim() === '') {
            categoriaService.cargarTodas();
            $scope.mostrarTodos = true;
            return;
        }

        categoriaService.buscar(nombre);
        $scope.mostrarTodos = false;
    };

    // Limpiar búsqueda
    $scope.limpiarBusqueda = function() {
        $scope.nombre = '';
        categoriaService.cargarTodas();
        $scope.mostrarTodos = true;
    };
});
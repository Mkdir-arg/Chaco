class DatabaseRouter:
    """Router para separar lecturas y escrituras"""
    
    def db_for_read(self, model, **hints):
        """Lecturas van a la réplica"""
        return 'replica'
    
    def db_for_write(self, model, **hints):
        """Escrituras van al master"""
        return 'default'
    
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """Solo migrar en la base principal"""
        return db == 'default'
from rfdetr import RFDETRMedium

model = RFDETRMedium()

# Check for various common attributes that store class names
class_names = None
if hasattr(model, 'names'):
    class_names = model.names
elif hasattr(model, 'class_names'):
    class_names = model.class_names
elif hasattr(model.model, 'names'):
    class_names = model.model.names
else:
    print("Could not find names attribute directly.")

if class_names:
    if isinstance(class_names, dict):
        print("Class Mapping (Dict):")
        for k, v in class_names.items():
            if v in ['person', 'cell phone', 'teddy bear', 'bicycle']:
                print(f"ID {k} -> {v}")
        
        # Check what is at ID 77, 67, 0, 1
        for cid in [0, 1, 67, 77]:
            if cid in class_names:
                 print(f"Check ID {cid} -> {class_names[cid]}")
    elif isinstance(class_names, list):
        print("Class Mapping (List):")
        for i, name in enumerate(class_names):
            if name in ['person', 'cell phone', 'teddy bear', 'bicycle']:
                print(f"ID {i} -> {name}")
                
        # Check what is at ID 77, 67, 0, 1
        for cid in [0, 1, 67, 77]:
            if cid < len(class_names):
                 print(f"Check ID {cid} -> {class_names[cid]}")

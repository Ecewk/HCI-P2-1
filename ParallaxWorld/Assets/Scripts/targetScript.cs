using UnityEngine;

public class targetScript : MonoBehaviour
{
    private static targetScript target;

    // Start is called once before the first execution of Update after the MonoBehaviour is created
    void Start()
    {
        
    }

    void Awake()
    {
        if (target == null) {
            target = this;
            DontDestroyOnLoad(target);
        }
        else {
            Destroy(gameObject);
        }
    } 

    // Update is called once per frame
    void Update()
    {
        
    }
}

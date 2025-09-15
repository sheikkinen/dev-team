#!/usr/bin/env python3
"""
Database CLI for face-changer pipeline

IMPORTANT: Changes via Change Management, see CLAUDE.md

Provides database management and querying capabilities
"""
import argparse
import sys
from pathlib import Path
from tabulate import tabulate
import json

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.models import get_database, get_job_model, get_pipeline_model

def cmd_status(args):
    """Show database status"""
    job_model = get_job_model()
    
    # Count jobs by status
    total = job_model.count_jobs()
    pending = job_model.count_jobs('pending')
    processing = job_model.count_jobs('processing')
    completed = job_model.count_jobs('completed')
    failed = job_model.count_jobs('failed')
    
    print(f"Database Status:")
    print(f"  Total jobs: {total}")
    print(f"  Pending: {pending}")
    print(f"  Processing: {processing}")
    print(f"  Completed: {completed}")
    print(f"  Failed: {failed}")
    
    # Add pony-flux job counts
    print(f"\nPony-Flux Jobs:")
    pf_counts = get_pony_flux_status_counts()
    print(f"  Total: {pf_counts['total']}")
    print(f"  Pending: {pf_counts['pending']}")
    print(f"  Processing: {pf_counts['processing']}")
    print(f"  Completed: {pf_counts['completed']}")
    print(f"  Failed: {pf_counts['failed']}")

def get_pony_flux_status_counts():
    """Get pony-flux job status counts"""
    from database.models import Database
    
    db = Database()
    counts = {'total': 0, 'pending': 0, 'processing': 0, 'completed': 0, 'failed': 0}
    
    try:
        with db._get_connection() as conn:
            # Total count
            cursor = conn.execute("SELECT COUNT(*) FROM pony_flux_jobs")
            counts['total'] = cursor.fetchone()[0]
            
            # Status counts
            for status in ['pending', 'processing', 'completed', 'failed']:
                cursor = conn.execute("SELECT COUNT(*) FROM pony_flux_jobs WHERE status = ?", (status,))
                counts[status] = cursor.fetchone()[0]
    except Exception as e:
        print(f"Error getting pony-flux counts: {e}")
    
    return counts

def cmd_list_pony_flux_jobs(args):
    """List pony-flux jobs"""
    from database.models import Database
    
    db = Database()
    
    try:
        with db._get_connection() as conn:
            query = "SELECT id, pony_prompt, flux_prompt, status, created_at, updated_at FROM pony_flux_jobs"
            params = []
            
            if args.status:
                query += " WHERE status = ?"
                params.append(args.status)
            
            query += " ORDER BY created_at DESC"
            
            if args.limit:
                query += " LIMIT ?"
                params.append(args.limit)
            
            cursor = conn.execute(query, params)
            jobs = cursor.fetchall()
        
        if not jobs:
            print("No pony-flux jobs found")
            return
        
        # Format for table display
        headers = ['ID', 'Status', 'Created', 'Pony Prompt', 'Flux Prompt']
        rows = []
        for job in jobs:
            job_id, pony_prompt, flux_prompt, status, created_at, updated_at = job
            created = created_at[:19] if created_at else ''
            pony_short = (pony_prompt[:25] + '...') if pony_prompt and len(pony_prompt) > 25 else pony_prompt
            flux_short = (flux_prompt[:25] + '...') if flux_prompt and len(flux_prompt) > 25 else flux_prompt
            rows.append([job_id, status, created, pony_short, flux_short])
        
        print(tabulate(rows, headers=headers, tablefmt='grid'))
        
    except Exception as e:
        print(f"Error listing pony-flux jobs: {e}")

def cmd_pony_flux_details(args):
    """Show detailed pony-flux job information"""
    from database.models import Database
    
    db = Database()
    
    try:
        with db._get_connection() as conn:
            cursor = conn.execute("""
                SELECT id, pony_prompt, flux_prompt, status, created_at, updated_at, metadata
                FROM pony_flux_jobs WHERE id = ?
            """, (args.job_id,))
            job = cursor.fetchone()
        
        if not job:
            print(f"Pony-flux job {args.job_id} not found")
            return
        
        job_id, pony_prompt, flux_prompt, status, created_at, updated_at, metadata = job
        
        print(f"Pony-Flux Job Details: {job_id}")
        print(f"  Status: {status}")
        print(f"  Pony Prompt: {pony_prompt}")
        print(f"  Flux Prompt: {flux_prompt}")
        print(f"  Created: {created_at}")
        print(f"  Updated: {updated_at}")
        if metadata:
            print(f"  Metadata: {metadata}")
        
        # Check for generated files
        print(f"\nGenerated Files:")
        from pathlib import Path
        
        # Check for pony image
        pony_file = Path(f"0-generated/{job_id}-pony.png")
        if pony_file.exists():
            print(f"  Pony image: {pony_file} ✅")
        else:
            print(f"  Pony image: {pony_file} ❌")
        
        # Check for scaled image
        scaled_file = Path(f"0-scaled/{job_id}-pony_upscaled.png")
        if scaled_file.exists():
            print(f"  Scaled image: {scaled_file} ✅")
        else:
            print(f"  Scaled image: {scaled_file} ❌")
        
        # Check for final result
        final_file = Path(f"6-final/{job_id}-make_this_person_more_attractive.png")
        if final_file.exists():
            print(f"  Final result: {final_file} ✅")
        else:
            print(f"  Final result: {final_file} ❌")
            
    except Exception as e:
        print(f"Error getting pony-flux job details: {e}")

def cmd_list_jobs(args):
    """List jobs"""
    job_model = get_job_model()
    jobs = job_model.list_jobs(status=args.status, limit=args.limit)
    
    if not jobs:
        print("No jobs found")
        return
    
    # Format for table display
    headers = ['ID', 'Status', 'Created', 'Image', 'Prompt']
    rows = []
    for job in jobs:
        created = job['created_at'][:19] if job['created_at'] else ''
        image_path = Path(job['input_image_path']).name if job['input_image_path'] else ''
        prompt = (job['user_prompt'][:30] + '...') if job['user_prompt'] and len(job['user_prompt']) > 30 else job['user_prompt']
        rows.append([job['job_id'], job['status'], created, image_path, prompt])
    
    print(tabulate(rows, headers=headers, tablefmt='grid'))

def cmd_job_details(args):
    """Show detailed job information"""
    job_model = get_job_model()
    pipeline_model = get_pipeline_model()
    
    job = job_model.get_job(args.job_id)
    if not job:
        print(f"Job {args.job_id} not found")
        return
    
    print(f"Job Details: {args.job_id}")
    print(f"  Status: {job['status']}")
    print(f"  Image: {job['input_image_path']}")
    print(f"  Prompt: {job['user_prompt']}")
    print(f"  Padding Factor: {job['padding_factor']}")
    print(f"  Mask Padding: {job['mask_padding_factor']}")
    print(f"  Created: {job['created_at']}")
    print(f"  Started: {job['started_at']}")
    print(f"  Completed: {job['completed_at']}")
    if job['error_message']:
        print(f"  Error: {job['error_message']}")
    
    # Show pipeline results
    results = pipeline_model.get_job_results(args.job_id)
    if results:
        print(f"\nPipeline Steps ({len(results)} completed):")
        for result in results:
            print(f"  {result['step_number']}. {result['step_name']} - {result['completed_at'][:19]}")
            if result['face_coordinates']:
                coords = result['face_coordinates']
                print(f"     Face coordinates: {coords}")
            if result['crop_dimensions']:
                dims = result['crop_dimensions']
                print(f"     Crop dimensions: {dims}")
            if result['file_paths']:
                paths = result['file_paths']
                print(f"     Files: {paths}")

def cmd_migrate_queue(args):
    """Migrate existing queue.json to database"""
    job_model = get_job_model()
    queue_file = Path("data/queue.json")
    
    if not queue_file.exists():
        print("No queue.json file found to migrate")
        return
    
    try:
        with open(queue_file) as f:
            queue_data = json.load(f)
        
        migrated = 0
        for item in queue_data.get('jobs', []):
            job_id = item.get('id')
            if job_id and 'input_image' in item:
                # Check if already exists
                existing = job_model.get_job(job_id)
                if not existing:
                    job_model.create_job(
                        job_id=job_id,
                        input_image_path=item['input_image'],
                        user_prompt=item.get('user_prompt', 'make this person more attractive')
                    )
                    migrated += 1
        
        print(f"Migrated {migrated} jobs from queue.json to database")
        
        if args.backup:
            import shutil
            shutil.move(queue_file, f"{queue_file}.backup")
            print(f"Backed up queue.json to {queue_file}.backup")
            
    except Exception as e:
        print(f"Migration failed: {e}")

def cmd_cleanup(args):
    """Clean up old jobs"""
    job_model = get_job_model()
    
    if args.status:
        # Clean up specific status
        jobs = job_model.list_jobs(status=args.status, limit=1000)
        if jobs:
            with job_model.db._get_connection() as conn:
                job_ids = [job['job_id'] for job in jobs]
                placeholders = ','.join(['?' for _ in job_ids])
                conn.execute(f"DELETE FROM pipeline_results WHERE job_id IN ({placeholders})", job_ids)
                conn.execute(f"DELETE FROM jobs WHERE job_id IN ({placeholders})", job_ids)
                conn.commit()
            print(f"Cleaned up {len(jobs)} jobs with status '{args.status}'")
        else:
            print(f"No jobs found with status '{args.status}'")
    else:
        print("Please specify --status for cleanup")

def cmd_cleanup_pony(args):
    """Clean up pony-flux jobs"""
    from database.models import Database
    
    db = Database()
    
    if args.status:
        # Clean up pony-flux jobs with specific status
        with db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM pony_flux_jobs WHERE status = ?", (args.status,))
            pony_jobs = cursor.fetchall()
            
            if pony_jobs:
                job_ids = [job[0] for job in pony_jobs]
                placeholders = ','.join(['?' for _ in job_ids])
                
                # Delete from pony_flux_jobs table
                cursor.execute(f"DELETE FROM pony_flux_jobs WHERE id IN ({placeholders})", job_ids)
                
                # Also clean up any related records in other tables
                cursor.execute(f"DELETE FROM pipeline_results WHERE job_id IN ({placeholders})", job_ids)
                cursor.execute(f"DELETE FROM jobs WHERE job_id IN ({placeholders})", job_ids)
                
                conn.commit()
                print(f"Cleaned up {len(job_ids)} pony-flux jobs with status '{args.status}'")
            else:
                print(f"No pony-flux jobs found with status '{args.status}'")
    else:
        # Clean up all pony-flux jobs
        with db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM pony_flux_jobs")
            pony_jobs = cursor.fetchall()
            
            if pony_jobs:
                job_ids = [job[0] for job in pony_jobs]
                placeholders = ','.join(['?' for _ in job_ids])
                
                # Delete from pony_flux_jobs table
                cursor.execute(f"DELETE FROM pony_flux_jobs WHERE id IN ({placeholders})", job_ids)
                
                # Also clean up any related records in other tables
                cursor.execute(f"DELETE FROM pipeline_results WHERE job_id IN ({placeholders})", job_ids)
                cursor.execute(f"DELETE FROM jobs WHERE job_id IN ({placeholders})", job_ids)
                
                conn.commit()
                print(f"Cleaned up {len(job_ids)} pony-flux jobs")
            else:
                print("No pony-flux jobs found")

def cmd_add_job(args):
    """Add a new job to the database"""
    import os
    
    # Validate input file exists
    if not os.path.exists(args.input_image):
        print(f"Error: Input image not found: {args.input_image}")
        return 1
    
    # Convert to absolute path
    abs_path = os.path.abspath(args.input_image)
    
    job_model = get_job_model()
    
    # Create the job
    try:
        db_id = job_model.create_job(
            job_id=args.job_id,
            input_image_path=abs_path,
            user_prompt=args.prompt,
            padding_factor=args.padding_factor,
            mask_padding_factor=args.mask_padding_factor
        )
        print(f"✅ Job created successfully!")
        print(f"   Job ID: {args.job_id}")
        print(f"   Database ID: {db_id}")
        print(f"   Input Image: {abs_path}")
        print(f"   Prompt: {args.prompt}")
        print(f"   Padding Factor: {args.padding_factor}")
        print(f"   Mask Padding Factor: {args.mask_padding_factor}")
        return 0
    except Exception as e:
        print(f"❌ Error creating job: {e}")
        return 1

def cmd_update_pony_flux_status(args):
    """Update pony-flux job status"""
    from database.models import Database
    
    db = Database()
    
    try:
        with db._get_connection() as conn:
            # Check if job exists
            cursor = conn.execute("SELECT id FROM pony_flux_jobs WHERE id = ?", (args.job_id,))
            if not cursor.fetchone():
                print(f"Pony-flux job {args.job_id} not found")
                return 1
            
            # Update status and completed timestamp
            if args.status == 'completed':
                conn.execute("""
                    UPDATE pony_flux_jobs 
                    SET status = ?, updated_at = CURRENT_TIMESTAMP 
                    WHERE id = ?
                """, (args.status, args.job_id))
            else:
                conn.execute("""
                    UPDATE pony_flux_jobs 
                    SET status = ?, updated_at = CURRENT_TIMESTAMP 
                    WHERE id = ?
                """, (args.status, args.job_id))
            
            conn.commit()
        
        print(f"✅ Updated pony-flux job {args.job_id} status to '{args.status}'")
        return 0
    except Exception as e:
        print(f"❌ Error updating job status: {e}")
        return 1

def cmd_remove_job(args):
    """Remove a job from the database"""
    job_model = get_job_model()
    pipeline_model = get_pipeline_model()
    
    # Check if job exists
    job = job_model.get_job(args.job_id)
    if not job:
        print(f"Job {args.job_id} not found")
        return 1
    
    try:
        # Remove pipeline results first
        with job_model.db._get_connection() as conn:
            conn.execute("DELETE FROM pipeline_results WHERE job_id = ?", (args.job_id,))
            conn.execute("DELETE FROM jobs WHERE job_id = ?", (args.job_id,))
            conn.commit()
        
        print(f"✅ Job {args.job_id} removed successfully!")
        print(f"   Reason: {args.reason or 'No reason specified'}")
        return 0
    except Exception as e:
        print(f"❌ Error removing job: {e}")
        return 1

def main():
    parser = argparse.ArgumentParser(description="Database CLI for face-changer pipeline")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Status command
    subparsers.add_parser('status', help='Show database status')
    
    # List jobs command
    list_parser = subparsers.add_parser('list', help='List jobs')
    list_parser.add_argument('--status', choices=['pending', 'processing', 'completed', 'failed'],
                           help='Filter by status')
    list_parser.add_argument('--limit', type=int, default=20, help='Limit number of results')
    
    # List pony-flux jobs command
    list_pf_parser = subparsers.add_parser('list-pony-flux', help='List pony-flux jobs')
    list_pf_parser.add_argument('--status', choices=['pending', 'processing', 'completed', 'failed'],
                               help='Filter by status')
    list_pf_parser.add_argument('--limit', type=int, default=20, help='Limit number of results')
    
    # Job details command
    details_parser = subparsers.add_parser('details', help='Show job details')
    details_parser.add_argument('job_id', help='Job ID to show details for')
    
    # Pony-flux job details command
    pf_details_parser = subparsers.add_parser('pony-flux-details', help='Show pony-flux job details')
    pf_details_parser.add_argument('job_id', help='Pony-flux job ID to show details for')
    
    # Migration command
    migrate_parser = subparsers.add_parser('migrate', help='Migrate queue.json to database')
    migrate_parser.add_argument('--backup', action='store_true', help='Backup original queue.json')
    
    # Cleanup command
    cleanup_parser = subparsers.add_parser('cleanup', help='Clean up old jobs')
    cleanup_parser.add_argument('--status', choices=['pending', 'processing', 'completed', 'failed'],
                               required=True, help='Status of jobs to clean up')
    
    # Cleanup pony command
    cleanup_pony_parser = subparsers.add_parser('cleanup-pony', help='Clean up pony-flux jobs')
    cleanup_pony_parser.add_argument('--status', choices=['pending', 'processing', 'completed', 'failed'],
                                   help='Status of pony-flux jobs to clean up (optional, clears all if not specified)')
    
    # Add job command
    add_job_parser = subparsers.add_parser('add-job', help='Add a new job to the database')
    add_job_parser.add_argument('job_id', help='Unique job identifier')
    add_job_parser.add_argument('input_image', help='Path to input image file')
    add_job_parser.add_argument('--prompt', default='make this person more attractive', 
                               help='AI prompt for face modification')
    add_job_parser.add_argument('--padding-factor', type=float, default=1.5,
                               help='Face crop padding factor (default: 1.5)')
    add_job_parser.add_argument('--mask-padding-factor', type=float, default=1.2,
                               help='Mask padding factor (default: 1.2)')
    
    # Remove job command
    remove_job_parser = subparsers.add_parser('remove-job', help='Remove a job from the database')
    remove_job_parser.add_argument('job_id', help='Job ID to remove')
    remove_job_parser.add_argument('--reason', help='Reason for removal (optional)')
    
    # Update pony-flux status command
    update_pf_parser = subparsers.add_parser('update-pony-flux-status', help='Update pony-flux job status')
    update_pf_parser.add_argument('job_id', help='Job ID to update')
    update_pf_parser.add_argument('status', choices=['pending', 'processing', 'completed', 'failed'],
                                 help='New status for the job')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == 'status':
            cmd_status(args)
        elif args.command == 'list':
            cmd_list_jobs(args)
        elif args.command == 'list-pony-flux':
            cmd_list_pony_flux_jobs(args)
        elif args.command == 'details':
            cmd_job_details(args)
        elif args.command == 'pony-flux-details':
            cmd_pony_flux_details(args)
        elif args.command == 'migrate':
            cmd_migrate_queue(args)
        elif args.command == 'cleanup':
            cmd_cleanup(args)
        elif args.command == 'cleanup-pony':
            cmd_cleanup_pony(args)
        elif args.command == 'add-job':
            return cmd_add_job(args)
        elif args.command == 'remove-job':
            return cmd_remove_job(args)
        elif args.command == 'update-pony-flux-status':
            return cmd_update_pony_flux_status(args)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()